import sqlite3

def safe_delete(cursor, table):
    try:
        cursor.execute(f"DELETE FROM {table};")
        print(f"✅ Cleared: {table}")
    except sqlite3.OperationalError as e:
        print(f"⚠️ Skipped {table}: {e}")

# Connect to the database
conn = sqlite3.connect("scores.db")
cursor = conn.cursor()

# Safely try deleting from both tables
safe_delete(cursor, "playoff_scores")
safe_delete(cursor, "playoff_matchups")

conn.commit()
conn.close()

print("🏁 Reset complete.")
