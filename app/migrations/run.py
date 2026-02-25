# app/migrations/run.py
import json
import os
import firebase_admin
from firebase_admin import credentials, firestore
from sqlalchemy import create_engine, text
from app.config import settings


def main():

    path = os.environ["FIREBASE_SERVICE_ACCOUNT_FILE"]

    cred = credentials.Certificate(path)

    firebase_admin.initialize_app(cred)
    db = firestore.client()

    docs = list(db.collection("creatures").limit(1).stream())

    doc_id = None
    doc_data = None
    for doc in docs:
        doc_id = doc.id
        doc_data = doc.to_dict()

    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)  

    CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS creatures (
        id TEXT PRIMARY KEY,
        data JSONB NOT NULL,
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    """

    CREATE_MIGRATION_TABLE_SQL="""
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
    INSERT INTO migration_state (job_name, collection, last_doc_id) VALUES (:job_name, :collection, :last_doc_id)
    ON CONFLICT (job_name) DO NOTHING;
    """

    UPDATE_TABLE_SQL = """
    INSERT INTO creatures (id, data, updated_at)
    VALUES (:id, CAST(:data AS JSONB), now())
    ON CONFLICT (id) DO UPDATE SET data = EXCLUDED.data, updated_at = EXCLUDED.updated_at;
    """

    SELECT_TABLE_SQL = """
    SELECT * FROM creatures WHERE id = :id;
    """

    UPDATE_STATE_SQL = """
    UPDATE migration_state SET last_doc_id = :last_doc_id, updated_at = now() WHERE job_name = :job_name;
    """

    with engine.begin() as conn:
        job_name = "firestore_creatures_to_postgres_v1"
        conn.execute(text(CREATE_TABLE_SQL))
        conn.execute(text(CREATE_MIGRATION_TABLE_SQL))

        checkpoint_row  = conn.execute(text(SELECT_STATE_SQL), {"job_name": job_name}).fetchone()
        print(f"checkpoint_row = {checkpoint_row}")
        if checkpoint_row is None: # This means there is no migration state fro this job in the database. We will insert an initial state with last_doc_id = None
             
            conn.execute(text(INSERT_STATE_SQL), {"job_name": job_name, "collection": "creatures", "last_doc_id": None})
 
        checkpoint_row = conn.execute(text(SELECT_STATE_SQL), {"job_name": job_name}).fetchone()
        print(f"checkpoint_row after insert = {checkpoint_row}")

        last_doc_id = checkpoint_row[0]  
       
        if last_doc_id is None:
            print("No last_doc_id found in migration_state. Starting from the beginning of the collection.")
            query = db.collection("creatures").order_by("__name__").limit(50)
            docs = list(query.stream())
            if len(docs) == 0:
                print("No documents found in Firestore collection. Exiting.")
                print(f"last_doc_id = {last_doc_id}")
                return
            first = docs[0]
            print(f"first.id = {first.id}, first.data = {first.to_dict()}")

            print(f"len(docs) = {len(docs)}")

            for doc in docs:
                doc_id = doc.id
                doc_data = doc.to_dict()
                conn.execute(text(UPDATE_TABLE_SQL), {"id": doc_id, "data": json.dumps(doc_data)})
                print(f"Upserted doc_id = {doc_id} into Postgres")
                last_doc_id = doc_id
                
            conn.execute(text(SELECT_TABLE_SQL), {"id": last_doc_id}).fetchone()
            conn.execute(text(UPDATE_STATE_SQL), {"last_doc_id": last_doc_id, "job_name": job_name})
        else:
            snapshot = db.collection("creatures").document(last_doc_id).get()
            query = db.collection("creatures").order_by("__name__").start_after(snapshot).limit(50)
            docs = list(query.stream())
            if len(docs) == 0:
                print("No new documents found in Firestore collection. Exiting.")
                print(f"last_doc_id = {last_doc_id}")
                return

            if len(docs) > 0:
                last_success_id = None
                for doc in docs:
                    doc_id = doc.id
                    doc_data = doc.to_dict()
                    conn.execute(text(UPDATE_TABLE_SQL), {"id": doc_id, "data": json.dumps(doc_data)})
                    last_success_id = doc_id

                print(f"last_success_id = {last_success_id}")
                conn.execute(text(UPDATE_STATE_SQL), {"last_doc_id": last_success_id, "job_name": job_name})
                conn.execute(text(SELECT_TABLE_SQL), {"id": last_success_id}).fetchone()


if __name__ == "__main__":
    main()
