import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import shutil
import os
from datetime import datetime

class ResetSeason(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="reset_season", description="Admin only: Archive and wipe all season data.")
    @app_commands.checks.has_role("Admin")
    async def reset_season(self, interaction: discord.Interaction):
        try:
            # Step 1: Archive scores.db
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_dir = "archive"
            os.makedirs(archive_dir, exist_ok=True)
            shutil.copy("scores.db", f"{archive_dir}/scores_backup_{timestamp}.db")

            # Step 2: Wipe relevant tables
            conn = sqlite3.connect("scores.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM scores")
            cursor.execute("DELETE FROM locks")
            # Removed the line that deletes team_codes since the table is missing
            cursor.execute("DROP TABLE IF EXISTS playoff_scores")
            cursor.execute("DROP TABLE IF EXISTS playoff_bracket")
            conn.commit()
            conn.close()

            await interaction.response.send_message(
                f"🧹 Season has been reset! Backup saved as `scores_backup_{timestamp}.db`.",
                ephemeral=True
            )

        except Exception as e:
            # If the interaction response was already sent, avoid sending another message
            if interaction.response.is_done():
                print(f"Interaction already responded, skipping further messages.")
                return
            await interaction.response.send_message(
                f"❌ Failed to reset season. Error: `{str(e)}`",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(ResetSeason(bot))
