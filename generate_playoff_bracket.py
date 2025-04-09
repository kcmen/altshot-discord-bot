import sqlite3

ROUND_MAP = {
    "q": "Quarterfinals",
    "quarterfinals": "Quarterfinals",
    "s": "Semifinals",
    "semifinals": "Semifinals",
    "f": "Finals",
    "finals": "Finals"
}

VALID_MATCHES = {
    "Quarterfinals": [1, 2, 3, 4],
    "Semifinals": [1, 2],
    "Finals": [1, 2]
}

def get_top_8_teams():
    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()

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

    sorted_teams = sorted(teams, key=lambda t: (-t[1], -t[2], t[0]))
    return sorted_teams[:8]

def generate_quarterfinals():
    top_8 = get_top_8_teams()
    if len(top_8) < 8:
        return None

    return [
        (top_8[0][0], top_8[7][0]),  # 1 vs 8
        (top_8[3][0], top_8[4][0]),  # 4 vs 5
        (top_8[1][0], top_8[6][0]),  # 2 vs 7
        (top_8[2][0], top_8[5][0])   # 3 vs 6
    ]

def get_winner(round_name, match_label):
    round_key = round_name.strip().lower()
    round_name = ROUND_MAP.get(round_key, round_name)

    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT winner FROM playoff_scores
        WHERE round = ? AND match = ?
    """, (round_name, str(match_label)))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def generate_semifinals_from_scores():
    w1 = get_winner("Quarterfinals", "1")
    w2 = get_winner("Quarterfinals", "2")
    w3 = get_winner("Quarterfinals", "3")
    w4 = get_winner("Quarterfinals", "4")

    if not all([w1, w2, w3, w4]):
        return None

    return [(w1, w2), (w3, w4)]

def generate_finals_from_scores():
    sf1 = get_winner("Semifinals", "1")
    sf2 = get_winner("Semifinals", "2")

    if not all([sf1, sf2]):
        return None

    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM playoff_scores WHERE round = 'Semifinals'
    """)
    matches = cursor.fetchall()
    conn.close()

    third_place = None
    if matches and len(matches) == 2:
        all_teams = []
        for match in matches:
            all_teams.extend([match[2], match[3]])
        losers = [team for team in all_teams if team and team not in [sf1, sf2]]
        if len(losers) == 2:
            third_place = (losers[0], losers[1])
        else:
            third_place = (sf2, sf1)
    else:
        third_place = (sf2, sf1)

    return {
        "Championship": (sf1, sf2),
        "Third Place": third_place
    }

