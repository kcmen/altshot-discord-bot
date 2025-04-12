import os
import shutil
import sqlite3
import json
from datetime import datetime
import discord
from discord.ext import commands
from discord import app_commands

class ResetSeason(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="reset_season", description="Archive and wipe all season data.")
    async def reset_season(self, interaction: discord.Interaction):
        try:
            # Step 1: Archive scores.db
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_dir = "archive"
            os.makedirs(archive_dir, exist_ok=True)
            shutil.copy("scores.db", f"{archive_dir}/scores_backup_{timestamp}.db")

            # Step 2: Wipe tables
            conn = sqlite3.connect("scores.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM scores")
            cursor.execute("DELETE FROM locks")
            cursor.execute("DELETE FROM flags")  # <-- this clears the 'pairings_posted' flag
            cursor.execute("DROP TABLE IF EXISTS playoff_scores")
            cursor.execute("DROP TABLE IF EXISTS playoff_bracket")
            conn.commit()
            conn.close()

            # Step 3: Reset week tracker to Week 1
            with open("week_tracker.json", "w") as f:
                json.dump({"current_week": 1}, f)

            await interaction.response.send_message(
                f"🧹 Season has been reset! Backup saved as `scores_backup_{timestamp}.db`.",
                ephemeral=True
            )

        except Exception as e:
            await interaction.response.send_message(
                f"❌ Failed to reset season. Error: `{str(e)}`",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(ResetSeason(bot))
