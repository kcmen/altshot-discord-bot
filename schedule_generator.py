import json
import random
from itertools import combinations

def load_teams():
    with open("teams.json", "r") as f:
        data = json.load(f)
    return list(data.keys())  # Only return team codes like T1, T2, etc.

def generate_limited_schedule(teams, max_weeks=8):
    total_matchups = list(combinations(teams, 2))
    random.shuffle(total_matchups)

    schedule = [[] for _ in range(max_weeks)]
    team_usage = {team: 0 for team in teams}

    for matchup in total_matchups:
        team1, team2 = matchup
        for week in schedule:
            teams_in_week = [t for match in week for t in match]
            if team1 not in teams_in_week and team2 not in teams_in_week:
                week.append((team1, team2))
                team_usage[team1] += 1
                team_usage[team2] += 1
                break

        if all(usage >= max_weeks for usage in team_usage.values()):
            break

    return schedule

def save_schedule(schedule):
    full_schedule = {}
    for week_num, matchups in enumerate(schedule, start=1):
        full_schedule[f"Week {week_num}"] = [
            {"team1": team1, "team2": team2} for team1, team2 in matchups
        ]
    with open("schedule.json", "w") as f:
        json.dump(full_schedule, f, indent=4)

if __name__ == "__main__":
    teams = load_teams()
    print(f"🔍 Loaded {len(teams)} teams: {teams}")
    schedule = generate_limited_schedule(teams)
    save_schedule(schedule)
    print(f"✅ Schedule generated for {len(teams)} teams and saved to schedule.json")
