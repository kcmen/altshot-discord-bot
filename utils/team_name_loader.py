import json

TEAM_FILE = "teams.json"

# Load team names from the JSON file
def load_team_names():
    try:
        with open(TEAM_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Get a team's full name, fallback to the raw team code (e.g. "T7")
def get_team_name(code):
    teams = load_team_names()
    return teams.get(code.upper(), code)
