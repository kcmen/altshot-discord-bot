# utils/playoff_utils.py

import sqlite3

def get_top_8_teams():
    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT team,
            SUM(CASE WHEN result IN ('W', '1UP', '2UP', '3&2', '4&3', '5&4') THEN 2
                     WHEN result IN ('AS', 'T') THEN 1
                     ELSE 0 END) AS points
        FROM scores
        GROUP BY team
        ORDER BY points DESC
        LIMIT 8
    """)
    top_teams = [row[0] for row in cursor.fetchall()]
    conn.close()
    return top_teams

def seed_playoff_teams(top_8):
    return {
        "Seed1": top_8[0],
        "Seed2": top_8[1],
        "Seed3": top_8[2],
        "Seed4": top_8[3],
        "Seed5": top_8[4],
        "Seed6": top_8[5],
        "Seed7": top_8[6],
        "Seed8": top_8[7],
    }
