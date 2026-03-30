from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "medical_ai.db"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    symptoms TEXT,
    doctor TEXT,
    test_type TEXT NOT NULL,
    disease TEXT NOT NULL,
    confidence REAL NOT NULL,
    risk_level TEXT NOT NULL,
    date TEXT NOT NULL,
    image_path TEXT,
    heatmap_path TEXT
);
"""


def init_database() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SCHEMA_SQL)
    print(f"Database initialized at {DB_PATH}")


if __name__ == "__main__":
    init_database()
