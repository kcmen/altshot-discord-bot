# commands/playoff_matchups.py

# Bracket structure using seed placeholders
PLAYOFF_MATCHUPS = {
    9: [  # Week 9 – Quarterfinals
        ("Seed1", "Seed8"),
        ("Seed4", "Seed5"),
        ("Seed2", "Seed7"),
        ("Seed3", "Seed6"),
    ],
    10: [  # Week 10 – Finals and 3rd place match
        ("Winner_QF1", "Winner_QF2"),  # Final
        ("Loser_QF1", "Loser_QF2"),    # 3rd place match
    ]
}
