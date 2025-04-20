from collections import defaultdict
from utils.team_name_loader import get_team_name

def format_leaderboard(rows):
    leaderboard = defaultdict(lambda: {"W": 0, "T": 0, "L": 0})

    for team, result in rows:
        team = team.upper().strip()
        if result == "AS":
            leaderboard[team]["T"] += 1
        elif result == "FORFEIT":
            leaderboard[team]["L"] += 1
        elif "&" in result:
            leaderboard[team]["W"] += 1

    for team in leaderboard:
        w, t, _ = leaderboard[team].values()
        leaderboard[team]["pts"] = (w * 2) + t

    sorted_leaderboard = sorted(
        leaderboard.items(),
        key=lambda x: (-x[1]["pts"], -x[1]["W"])
    )

    output = ""
    for team_code, stats in sorted_leaderboard:
        name = get_team_name(team_code)
        output += f"{name}: {stats['pts']} pts (W:{stats['W']} T:{stats['T']} L:{stats['L']})\n"

    return output.strip()
