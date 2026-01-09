import psycopg2
from contextlib import contextmanager
from app.config import settings


@contextmanager
def get_db_connection():
    conn = None
    try:
        conn = psycopg2.connect(settings.DATABASE_URL)
        yield conn
        conn.commit()
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()