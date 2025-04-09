import sqlite3

WEEK_TO_UNLOCK = 1  # Change this to the week you want to unlock

conn = sqlite3.connect("scores.db")
cursor = conn.cursor()

cursor.execute("UPDATE locks SET locked = 0 WHERE week = ?", (WEEK_TO_UNLOCK,))
conn.commit()
conn.close()

print(f"🔓 Week {WEEK_TO_UNLOCK} is now unlocked.")
