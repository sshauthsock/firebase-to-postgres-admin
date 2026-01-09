import json
from typing import Optional, Dict, List
from psycopg2.extras import RealDictCursor
from app.database import get_db_connection


def get_all_creatures(
    name: Optional[str] = None,
    grade: Optional[str] = None,
    type: Optional[str] = None,
    influence: Optional[str] = None
) -> List[Dict]:
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        query = "SELECT * FROM Creatures"
        conditions = []
        params = []
        
        if name:
            conditions.append("name = %s")
            params.append(name)
        if grade:
            conditions.append("grade = %s")
            params.append(grade)
        if type:
            conditions.append("type = %s")
            params.append(type)
        if influence:
            conditions.append("influence = %s")
            params.append(influence)
            
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        cur.execute(query, params)
        creatures = cur.fetchall()
        cur.close()
        return list(creatures)


def get_creature_by_id(creature_id: int) -> Optional[Dict]:
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("SELECT * FROM Creatures WHERE id = %s", (creature_id,))
        creature = cur.fetchone()
        
        if creature:
            cur.execute("""
                SELECT level, bindStat, registrationStat 
                FROM Creature_Level_Stats 
                WHERE creature_id = %s 
                ORDER BY level ASC
            """, (creature_id,))
            creature["stats"] = cur.fetchall()
        
        cur.close()
        return dict(creature) if creature else None


def create_creature(creature_data: Dict) -> int:
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        try:
            cur.execute(
                """INSERT INTO Creatures (name, grade, type, influence, image) 
                   VALUES (%s, %s, %s, %s, %s) RETURNING id""",
                (
                    creature_data["name"],
                    creature_data["grade"],
                    creature_data["type"],
                    creature_data["influence"],
                    creature_data["image"]
                )
            )
            new_id = cur.fetchone()[0]
            
            cur.execute(
                """INSERT INTO Creature_Level_Stats (creature_id, level, bindStat, registrationStat) 
                   VALUES (%s, %s, %s, %s)""",
                (
                    new_id,
                    0,
                    json.dumps(creature_data.get("initial_bindStat", {})),
                    json.dumps(creature_data.get("initial_registrationStat", {}))
                )
            )
            
            cur.close()
            return new_id
        except Exception:
            cur.close()
            raise


def update_creature(creature_id: int, updates: Dict) -> bool:
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        if not updates:
            cur.close()
            return False
            
        set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
        values = list(updates.values())
        values.append(creature_id)
        
        cur.execute(f"UPDATE Creatures SET {set_clause} WHERE id = %s", values)
        result = cur.rowcount > 0
        cur.close()
        return result


def delete_creature(creature_id: int) -> bool:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM Creatures WHERE id = %s", (creature_id,))
        result = cur.rowcount > 0
        cur.close()
        return result


def create_or_update_level_stats(stats_data: Dict) -> bool:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Creature_Level_Stats (creature_id, level, bindStat, registrationStat) 
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (creature_id, level)
            DO UPDATE SET
                bindStat = EXCLUDED.bindStat,
                registrationStat = EXCLUDED.registrationStat;
        """, (
            stats_data["creature_id"],
            stats_data["level"],
            json.dumps(stats_data.get("bindStat", {})),
            json.dumps(stats_data.get("registrationStat", {}))
        ))
        cur.close()
        return True

