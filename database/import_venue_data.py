import sqlite3
import pandas as pd
from database.connection import DB_PATH, BASE_DIR

def import_venue_data():
    venues_path = BASE_DIR / "data" / "venues.csv"
    complexes_path = BASE_DIR / "data" / "complexes.csv"
    venues_df = pd.read_csv(venues_path)
    complexes_df = pd.read_csv(complexes_path)
    conn = sqlite3.connect(str(DB_PATH))
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS Complexes (
                complex_id TEXT PRIMARY KEY,
                complex_name TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS Venues (
                venue_id TEXT PRIMARY KEY,
                venue_name TEXT NOT NULL,
                city_name TEXT NOT NULL,
                country_name TEXT NOT NULL,
                country_code TEXT NOT NULL,
                timezone TEXT NOT NULL,
                complex_id TEXT NOT NULL,
                FOREIGN KEY (complex_id)
                    REFERENCES Complexes(complex_id)
            )
        """)

        # Insert only new records; do not overwrite existing records.
        conn.executemany("""
            INSERT OR IGNORE INTO Complexes
            (complex_id, complex_name)
            VALUES (?, ?)
        """, complexes_df.itertuples(index=False, name=None))

        conn.executemany("""
            INSERT OR IGNORE INTO Venues
            (venue_id, venue_name, city_name, country_name,
             country_code, timezone, complex_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, venues_df.itertuples(index=False, name=None))

        # Verify foreign key relationships
        violations = conn.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        if violations:
            raise ValueError(f"Foreign key violations found: {violations[:5]}")
        
        conn.commit()

        print("\nVENUE DATA IMPORT SUCCESSFUL")
        print("Complexes:", conn.execute(
            "SELECT COUNT(*) FROM Complexes"
        ).fetchone()[0])
        print("Venues:", conn.execute(
            "SELECT COUNT(*) FROM Venues"
        ).fetchone()[0])

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    import_venue_data()
