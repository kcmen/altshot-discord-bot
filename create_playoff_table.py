import sqlite3

conn = sqlite3.connect("scores.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS playoff_scores (
    round TEXT,
    match TEXT,
    team1 TEXT,
    team2 TEXT,
    winner TEXT,
    UNIQUE(round, match)
)
""")

conn.commit()
conn.close()
print("✅ playoff_scores table created.")
