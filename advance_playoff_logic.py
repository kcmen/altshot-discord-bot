import sqlite3

# Get recorded winner for a specific playoff round and match
def get_winner(round_name, match_label):
    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT winner FROM playoff_scores
        WHERE round = ? AND match = ?
    """, (round_name, match_label))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

# Get all QF results and generate semifinal matchups
def generate_semifinals_from_scores():
    w1 = get_winner("Quarterfinals", "QF1")
    w2 = get_winner("Quarterfinals", "QF2")
    w3 = get_winner("Quarterfinals", "QF3")
    w4 = get_winner("Quarterfinals", "QF4")

    if not all([w1, w2, w3, w4]):
        return None

    return [(w1, w2), (w3, w4)]

# Get all SF results and generate finals matchups
def generate_finals_from_scores():
    w1 = get_winner("Semifinals", "SF1")
    w2 = get_winner("Semifinals", "SF2")

    if not all([w1, w2]):
        return None

    return {
        "Championship": (w1, w2),
        "Third Place": (w2, w1)  # loser logic handled elsewhere
    }
