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
