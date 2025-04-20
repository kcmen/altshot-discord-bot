import discord
from discord import app_commands
from utils.week_tracker import get_current_week
from utils.team_name_loader import get_team_name  # ✅ Needed for team name display

# Hardcoded matchups for 8-week round robin
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

@app_commands.command(name="schedule", description="View full 8-week Alt Shot match schedule")
async def schedule(interaction: discord.Interaction):
    lines = []
    for week, matchups in MATCHUPS_BY_WEEK.items():
        lines.append(f"📅 **Week {week}**")
        for t1, t2 in matchups:
            team1 = get_team_name(t1)
            team2 = get_team_name(t2)
            lines.append(f"• {team1} vs {team2}")
        lines.append("")  # Blank line between weeks

    output = "\n".join(lines)
    await interaction.response.send_message(output)

async def setup(bot):
    bot.tree.add_command(schedule)
