# app/migrations/run.py
import json
import os

import firebase_admin
from firebase_admin import credentials, firestore

from sqlalchemy import create_engine, text

from app.config import settings


BATCH_SIZE = 50
COLLECTION = "creatures"
JOB_NAME = "firestore_creatures_to_postgres_v1"


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS creatures (
    id TEXT PRIMARY KEY,
    data JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""

CREATE_MIGRATION_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS migration_state (
    job_name TEXT PRIMARY KEY,
    collection TEXT NOT NULL,
    last_doc_id TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""

SELECT_STATE_SQL = """
SELECT last_doc_id FROM migration_state WHERE job_name = :job_name;
"""

INSERT_STATE_SQL = """
INSERT INTO migration_state (job_name, collection, last_doc_id)
VALUES (:job_name, :collection, :last_doc_id)
ON CONFLICT (job_name) DO NOTHING;
"""

UPSERT_CREATURE_SQL = """
INSERT INTO creatures (id, data, updated_at)
VALUES (:id, CAST(:data AS JSONB), now())
ON CONFLICT (id) DO UPDATE
SET data = EXCLUDED.data, updated_at = EXCLUDED.updated_at;
"""

UPDATE_STATE_SQL = """
UPDATE migration_state
SET last_doc_id = :last_doc_id, updated_at = now()
WHERE job_name = :job_name;
"""


def init_firestore():
    print("Initializing Firestore client...")

    # Standard env var (preferred in Docker)
    path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "serviceAccountKey.json")
    print(f"Using service account file: {path}")

    cred = credentials.Certificate(path)

    # Avoid double-init error if main() is invoked multiple times in same process
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)

    return firestore.client()


def verify_counts_on_finish(db, conn):
    """
    Run only when migration is finished (no docs left).
    For <10k docs, streaming count is fast and the most compatible.
    """
    print(" Migration finished. Verifying counts...")

    fs_count = sum(1 for _ in db.collection(COLLECTION).stream())
    pg_count = conn.execute(text("SELECT COUNT(*) FROM creatures;")).scalar_one()

    print(f"Firestore {COLLECTION} count = {fs_count}")
    print(f"Postgres  {COLLECTION} count = {pg_count}")
    print(f"Count match? {fs_count == pg_count}")


def ensure_state_row(conn):
    # Create tables
    conn.execute(text(CREATE_TABLE_SQL))
    conn.execute(text(CREATE_MIGRATION_TABLE_SQL))

    # Ensure row exists (idempotent)
    checkpoint_row = conn.execute(text(SELECT_STATE_SQL), {"job_name": JOB_NAME}).fetchone()
    if checkpoint_row is None:
        conn.execute(
            text(INSERT_STATE_SQL),
            {"job_name": JOB_NAME, "collection": COLLECTION, "last_doc_id": None},
        )


def get_last_doc_id(conn):
    row = conn.execute(text(SELECT_STATE_SQL), {"job_name": JOB_NAME}).fetchone()
    return row[0]  # may be None


def fetch_batch(db, last_doc_id):
    if last_doc_id is None:
        print("No last_doc_id found. Starting from beginning.")
        query = db.collection(COLLECTION).order_by("__name__").limit(BATCH_SIZE)
        return list(query.stream())

    snapshot = db.collection(COLLECTION).document(last_doc_id).get()
    query = (
        db.collection(COLLECTION)
        .order_by("__name__")
        .start_after(snapshot)
        .limit(BATCH_SIZE)
    )
    return list(query.stream())


def upsert_batch(conn, docs):
    """
    Upsert all docs and return the last successfully processed document id.
    """
    last_success_id = None
    for doc in docs:
        doc_id = doc.id
        doc_data = doc.to_dict()
        conn.execute(text(UPSERT_CREATURE_SQL), {"id": doc_id, "data": json.dumps(doc_data)})
        last_success_id = doc_id

    return last_success_id


def main():
    db = init_firestore()

    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

    with engine.begin() as conn:
        ensure_state_row(conn)

        last_doc_id = get_last_doc_id(conn)
        print(f"Current checkpoint last_doc_id = {last_doc_id}")

        docs = fetch_batch(db, last_doc_id)

        # Finished / nothing to do
        if len(docs) == 0:
            if last_doc_id is None:
                print("No documents found in Firestore collection. Nothing to migrate.")
            else:
                print("No new documents found. Migration appears complete.")

            verify_counts_on_finish(db, conn)
            return

        print(f"Fetched {len(docs)} docs (batch_size={BATCH_SIZE})")

        last_success_id = upsert_batch(conn, docs)
        print(f"Batch upsert complete. last_success_id = {last_success_id}")

        # Checkpoint update only after batch succeeds (crash-safe)
        conn.execute(text(UPDATE_STATE_SQL), {"last_doc_id": last_success_id, "job_name": JOB_NAME})
        print(f"Checkpoint updated to last_doc_id = {last_success_id}")


if __name__ == "__main__":
    main()