ROUND_MAP = {
    "q": "Quarterfinals",
    "quarterfinals": "Quarterfinals",
    "s": "Semifinals",
    "semifinals": "Semifinals",
    "f": "Finals",
    "finals": "Finals"
}

def normalize_round_name(input_name):
    return ROUND_MAP.get(input_name.strip().lower(), input_name)
