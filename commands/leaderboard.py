import sqlite3
import discord
from discord.ext import commands
from discord import app_commands
from utils.week_tracker import get_current_week

LEADERBOARD_CHANNEL_ID = 1356054289650417889  # #leaderboard

async def post_leaderboard(bot):
    print("📊 post_leaderboard() function triggered.")  # Log when function runs

    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()

    # Get all scores
    cursor.execute("SELECT team, result FROM scores")
    results = cursor.fetchall()
    conn.close()

    # Track standings and hole differential
    standings = {}
    holes = {}

    for team, result in results:
        if result == "AS":
            standings[team] = standings.get(team, 0) + 0.5
        elif result == "FORFEIT":
            standings[team] = standings.get(team, 0)
        else:
            try:
                up, _ = map(int, result.split("&"))
                standings[team] = standings.get(team, 0) + 1
                holes[team] = holes.get(team, 0) + up
            except:
                continue

    sorted_teams = sorted(standings.items(), key=lambda x: (-x[1], -holes.get(x[0], 0)))

    lines = ["🏆 **LCS Alt Shot Leaderboard**"]
    for i, (team, points) in enumerate(sorted_teams, 1):
        hole_diff = holes.get(team, 0)
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else ""
        lines.append(f"{medal} {team}: {points} pts | +{hole_diff} holes")

    message = "\n".join(lines)
    channel = bot.get_channel(LEADERBOARD_CHANNEL_ID)
    if channel:
        await channel.send(message)

# Register leaderboard command (optional)
class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="update_leaderboard", description="Force post the leaderboard (Admin only)")
    async def update_leaderboard(self, interaction: discord.Interaction):
        await post_leaderboard(interaction.client)
        await interaction.response.send_message("📊 Leaderboard has been updated.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))

