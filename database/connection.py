import sqlite3
from pathlib import Path

# ==========================================
# DATABASE CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "tennis_rankings.db"

# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_connection():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_PATH}"
        )
    conn = sqlite3.connect(
        str(DB_PATH),
        check_same_thread=False
    )
    return conn

# ==========================================
# GET ALL DATABASE TABLES
# ==========================================

def get_tables():
    conn = get_connection()
    try:
        query = """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name;
        """
        result = conn.execute(query).fetchall()
        return [row[0] for row in result]
    finally:
        conn.close()


# ==========================================
# GET TABLE RECORD COUNT
# ==========================================

def get_table_count(table_name):
    allowed_tables = get_tables()
    if table_name not in allowed_tables:
        raise ValueError("Invalid table name")
    conn = get_connection()
    try:
        query = f'SELECT COUNT(*) FROM "{table_name}"'
        result = conn.execute(query).fetchone()
        return result[0]
    finally:
        conn.close()


# ==========================================
# DATABASE TEST
# ==========================================

if __name__ == "__main__":
    print("\n================================")
    print("TENNIS ANALYTICS DATABASE TEST")
    print("================================\n")

    print("Database Path:", DB_PATH)
    print("\nAvailable Tables:")

    for table in get_tables():
        count = get_table_count(table)
        print(f"{table}: {count} records")
    print("\nDatabase Connection Successful!")
