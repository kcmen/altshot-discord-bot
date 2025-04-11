import json
import random
from itertools import combinations

def load_teams():
    with open("teams.json", "r") as f:
        data = json.load(f)

    # Corrected: Use all player names from the keys of the JSON (which are names)
    clean_players = list(data.keys())
    return clean_players

def create_teams(players):
    random.shuffle(players)
    if len(players) % 2 != 0:
        raise ValueError("Player count is not even. Cannot create valid 2-person teams.")
    return [(players[i], players[i+1]) for i in range(0, len(players), 2)]

def generate_round_robin(teams):
    if len(teams) % 2:
        teams.append(("BYE", "BYE"))  # odd number of teams

    num_rounds = len(teams) - 1
    schedule = []

    for round_num in range(num_rounds):
        round_matches = []
        for i in range(len(teams) // 2):
            team1 = teams[i]
            team2 = teams[-i-1]
            round_matches.append((team1, team2))
        schedule.append(round_matches)
        teams.insert(1, teams.pop())  # rotate teams

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
    players = load_teams()
    teams = create_teams(players)
    schedule = generate_round_robin(teams)
    save_schedule(schedule)
    print(f"✅ Schedule generated for {len(teams)} teams and saved to schedule.json")
