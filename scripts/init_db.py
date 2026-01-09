import psycopg2
from app.config import settings

def get_db_connection():
    return psycopg2.connect(settings.DATABASE_URL)

def init_db():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("DROP TABLE IF EXISTS Creature_Level_Stats CASCADE;")
        cur.execute("DROP TABLE IF EXISTS Creatures CASCADE;")

        cur.execute("""
            CREATE TABLE Creatures (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                grade VARCHAR(50) NOT NULL,
                type VARCHAR(50) NOT NULL,
                influence VARCHAR(50) NOT NULL,
                image TEXT
            );
        """)

        cur.execute("""
            CREATE TABLE Creature_Level_Stats (
                creature_id INTEGER REFERENCES Creatures(id) ON DELETE CASCADE,
                level INTEGER NOT NULL CHECK (level >= 0 AND level <= 25),
                bindStat JSONB DEFAULT '{}',
                registrationStat JSONB DEFAULT '{}',
                PRIMARY KEY (creature_id, level)
            );
        """)

        conn.commit()
        print("Database initialized successfully!")
        cur.close()
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error initializing database: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    init_db()