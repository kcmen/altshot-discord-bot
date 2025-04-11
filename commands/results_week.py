import time
import sqlite3
import discord
from discord import app_commands
from discord.ext import commands

# Retry logic for database locked error
def execute_query_with_retry(query, params=None, max_retries=3, retry_delay=2):
    retries = 0
    while retries < max_retries:
        try:
            conn = sqlite3.connect("scores.db", timeout=10)  # Set timeout for 10 seconds
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            conn.commit()
            conn.close()
            return True  # Success
        except sqlite3.OperationalError as e:
            if 'locked' in str(e).lower():
                retries += 1
                print(f"Database locked, retrying {retries}/{max_retries}...")
                time.sleep(retry_delay)
            else:
                raise  # Raise other types of errors
    return False  # Fail after retries

class AdminTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="reset_week", description="Admin only: Delete all scores for a specific week.")
    @app_commands.checks.has_role("Admin")
    async def reset_week(self, interaction: discord.Interaction, week: int):
        # Attempt to reset the scores with retry mechanism
        if execute_query_with_retry("DELETE FROM scores WHERE week = ?", (week,)):
            await interaction.response.send_message(f"🗑️ All scores for **Week {week}** have been cleared.", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Failed to reset scores for Week {week}. Database was locked.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdminTools(bot))
