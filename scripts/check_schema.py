import psycopg2
from app.config import settings
from psycopg2.extras import RealDictCursor

def check_schema():
    conn = None
    try:
        conn = psycopg2.connect(settings.DATABASE_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT 
                constraint_name,
                table_name,
                column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.constraint_column_usage ccu
                ON tc.constraint_name = ccu.constraint_name
            WHERE tc.table_name = 'creatures'
                AND tc.constraint_type = 'UNIQUE'
        """)
        
        constraints = cur.fetchall()
        
        print("Unique constraints on Creatures table:")
        if constraints:
            for constraint in constraints:
                print(f"  - {constraint['constraint_name']} on {constraint['column_name']}")
        else:
            print("  No unique constraints found")
        
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'creatures'
            ORDER BY ordinal_position
        """)
        
        columns = cur.fetchall()
        
        print("\nCreatures table columns:")
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        
        cur.close()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_schema()

