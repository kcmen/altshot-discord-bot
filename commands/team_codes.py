import discord
from discord import app_commands
from datetime import datetime
from utils.team_name_loader import get_team_name

# Official Alt Shot Match Schedule for 20 teams (Weeks 1–8)
MATCHUPS_BY_WEEK = {
    1: [("T1", "T2"), ("T3", "T4"), ("T5", "T6"), ("T7", "T8"), ("T9", "T10"),
        ("T11", "T12"), ("T13", "T14"), ("T15", "T16"), ("T17", "T18"), ("T19", "T20")],
    2: [("T1", "T3"), ("T2", "T4"), ("T5", "T7"), ("T6", "T8"), ("T9", "T11"),
        ("T10", "T12"), ("T13", "T15"), ("T14", "T16"), ("T17", "T19"), ("T18", "T20")],
    3: [("T1", "T4"), ("T2", "T5"), ("T3", "T6"), ("T7", "T9"), ("T8", "T10"),
        ("T11", "T13"), ("T12", "T14"), ("T15", "T17"), ("T16", "T18"), ("T19", "T20")],
    4: [("T1", "T5"), ("T2", "T6"), ("T3", "T7"), ("T4", "T8"), ("T9", "T13"),
        ("T10", "T14"), ("T11", "T15"), ("T12", "T16"), ("T17", "T20"), ("T18", "T19")],
    5: [("T1", "T6"), ("T2", "T7"), ("T3", "T8"), ("T4", "T9"), ("T5", "T10"),
        ("T11", "T16"), ("T12", "T15"), ("T13", "T18"), ("T14", "T17"), ("T19", "T20")],
    6: [("T1", "T7"), ("T2", "T8"), ("T3", "T9"), ("T4", "T10"), ("T5", "T11"),
        ("T6", "T12"), ("T13", "T19"), ("T14", "T20"), ("T15", "T17"), ("T16", "T18")],
    7: [("T1", "T8"), ("T2", "T9"), ("T3", "T10"), ("T4", "T11"), ("T5", "T12"),
        ("T6", "T13"), ("T7", "T14"), ("T15", "T20"), ("T16", "T19"), ("T17", "T18")],
    8: [("T1", "T9"), ("T2", "T10"), ("T3", "T11"), ("T4", "T12"), ("T5", "T13"),
        ("T6", "T14"), ("T7", "T15"), ("T8", "T16"), ("T17", "T20"), ("T18", "T19")],
}

# Automatically calculate current week from season start
SEASON_START = datetime(2025, 4, 14, 0, 0, 0)  # Midnight GMT

def get_current_week():
    now = datetime.utcnow()
    delta = now - SEASON_START
    week = delta.days // 7 + 1
    return max(1, min(week, 10))  # clamp to valid range

@app_commands.command(name="team_matchup", description="Find your opponent for the current week")
@app_commands.describe(team="Your team name (e.g. T5)")
async def team_matchup(interaction: discord.Interaction, team: str):
    team = team.strip().upper()
    week = get_current_week()
    matchups = MATCHUPS_BY_WEEK.get(week)

    if not matchups:
        await interaction.response.send_message(f"\U0001F4C6 No matchups found for Week {week}.", ephemeral=True)
        return

    for t1, t2 in matchups:
        if team == t1 or team == t2:
            opponent = t2 if team == t1 else t1
            name1 = get_team_name(t1)
            name2 = get_team_name(t2)
            await interaction.response.send_message(f"\U0001F4CC **Week {week} Matchup:**\n\U0001F7E2 *{name1} ({t1})* vs \U0001F535 *{name2} ({t2})*")
            return

    await interaction.response.send_message(f"❌ No matchup found for team {team} in Week {week}.", ephemeral=True)

# Register
async def setup(bot):
    bot.tree.add_command(team_matchup)
