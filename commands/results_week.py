import sqlite3
import discord
from discord import app_commands, Interaction
from discord.ext import commands

class ResultsWeek(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="results_week", description="See all match results for a specific week")
    @app_commands.describe(week="Week number to view results for")
    async def results_week(self, interaction: Interaction, week: int):
        try:
            conn = sqlite3.connect("scores.db")
            cursor = conn.cursor()
            cursor.execute("SELECT team, result FROM scores WHERE week = ?", (week,))
            results = cursor.fetchall()
            conn.close()

            if not results:
                await interaction.response.send_message(f"\U0001F4ED No scores reported for Week {week}.")
            else:
                msg = f"\U0001F4CA **Results for Week {week}:**\n"
                for team, result in results:
                    msg += f"`{team}`: {result}\n"
                await interaction.response.send_message(msg)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error fetching results: {e}")

async def setup(bot):
    await bot.add_cog(ResultsWeek(bot))
