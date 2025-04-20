import sqlite3
import discord
from discord import app_commands, Interaction
from discord.ext import commands

class HoleDiff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hole_diff", description="Show total holes won by each team")
    async def hole_diff(self, interaction: Interaction):
        try:
            conn = sqlite3.connect("scores.db")
            cursor = conn.cursor()
            cursor.execute("SELECT team, result FROM scores")
            rows = cursor.fetchall()
            conn.close()

            diffs = {}
            for team, result in rows:
                if team not in diffs:
                    diffs[team] = 0
                if "&" in result:
                    n = int(result.split("&")[0])
                    diffs[team] += n

            sorted_diffs = sorted(diffs.items(), key=lambda x: x[1], reverse=True)
            msg = "\U0001F9AE **Hole Differential by Team**\n"
            for team, diff in sorted_diffs:
                msg += f"{team}: +{diff}\n"
            await interaction.response.send_message(msg)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error fetching hole differentials: {e}")

async def setup(bot):
    await bot.add_cog(HoleDiff(bot))
