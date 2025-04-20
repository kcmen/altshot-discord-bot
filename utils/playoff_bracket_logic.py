# playoff_bracket_logic.py

import sqlite3

def get_top_8_teams():
    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()

    # Get scores aggregated by team
    cursor.execute("""
        SELECT team,
               SUM(CASE WHEN result LIKE '%&%' THEN 2 
                        WHEN result LIKE 'AS' THEN 1 ELSE 0 END) AS pts,
               SUM(CASE WHEN result LIKE '%&%' THEN 1 ELSE 0 END) AS wins,
               SUM(CASE WHEN result LIKE 'AS' THEN 1 ELSE 0 END) AS ties,
               SUM(CASE WHEN result LIKE 'L%' THEN 1 ELSE 0 END) AS losses
        FROM scores
        GROUP BY team
    """)

    teams = cursor.fetchall()
    conn.close()

    # Sort by pts -> wins -> team name
    sorted_teams = sorted(
        teams,
        key=lambda t: (-t[1], -t[2], t[0])
    )

    return sorted_teams[:8]  # Return top 8


def generate_playoff_bracket():
    top_8 = get_top_8_teams()
    bracket = []

    # Quarterfinals: 1v8, 2v7, 3v6, 4v5
    bracket.append((top_8[0][0], top_8[7][0]))
    bracket.append((top_8[3][0], top_8[4][0]))
    bracket.append((top_8[1][0], top_8[6][0]))
    bracket.append((top_8[2][0], top_8[5][0]))

    return bracket
