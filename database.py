import sqlite3
from datetime import datetime

# Connect to (or create) the scores database
conn = sqlite3.connect("scores.db")
cursor = conn.cursor()

# Create the scores table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team TEXT NOT NULL,
    result TEXT NOT NULL,
    week INTEGER NOT NULL,
    submitted_by TEXT NOT NULL,
    timestamp TEXT NOT NULL
)
""")

conn.commit()
conn.close()
