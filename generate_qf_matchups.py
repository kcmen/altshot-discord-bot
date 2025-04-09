import sqlite3
from generate_playoff_bracket import get_top_8_teams

def generate_qf_matchups():
    teams = get_top_8_teams()
    if len(teams) < 8:
        print("❌ Not enough teams to generate quarterfinals.")
        return

    matchups = [
        ("QF1", teams[0][0], teams[7][0]),  # 1 vs 8
        ("QF2", teams[3][0], teams[4][0]),  # 4 vs 5
        ("QF3", teams[1][0], teams[6][0]),  # 2 vs 7
        ("QF4", teams[2][0], teams[5][0])   # 3 vs 6
    ]

    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS playoff_matchups (
            round TEXT,
            match TEXT,
            team1 TEXT,
            team2 TEXT,
            PRIMARY KEY (round, match)
        )
    """)

    for match_label, t1, t2 in matchups:
        cursor.execute("""
            INSERT OR REPLACE INTO playoff_matchups (round, match, team1, team2)
            VALUES (?, ?, ?, ?)
        """, ("Quarterfinals", match_label, t1, t2))

    conn.commit()
    conn.close()
    print("✅ Quarterfinal matchups saved to playoff_matchups table.")

if __name__ == "__main__":
    generate_qf_matchups()
