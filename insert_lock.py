import sqlite3

conn = sqlite3.connect("scores.db")
cursor = conn.cursor()

# Make sure 'locked' column exists
cursor.execute("PRAGMA table_info(locks)")
columns = [col[1] for col in cursor.fetchall()]

if "locked" not in columns:
    print("➕ Adding 'locked' column to locks table...")
    cursor.execute("ALTER TABLE locks ADD COLUMN locked INTEGER DEFAULT 0")
else:
    print("✅ 'locked' column already exists.")

# Now insert or update week 1 as locked
cursor.execute("REPLACE INTO locks (week, locked) VALUES (?, ?)", (1, 1))

conn.commit()
conn.close()
print("🔒 Week 1 is now locked.")
