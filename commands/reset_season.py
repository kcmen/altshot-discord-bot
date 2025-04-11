import discord
import sqlite3
import os
import shutil
from discord import app_commands
from discord.ext import commands
from datetime import datetime

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

            # Step 2: Wipe or drop tables
            conn = sqlite3.connect("scores.db")
            cursor = conn.cursor()

            # Delete rows from known tables
            cursor.execute("DELETE FROM scores")
            cursor.execute("DELETE FROM locks")

            # Drop tables that may or may not exist
            cursor.execute("DROP TABLE IF EXISTS team_codes")
            cursor.execute("DROP TABLE IF EXISTS playoff_scores")
            cursor.execute("DROP TABLE IF EXISTS playoff_bracket")

            conn.commit()
            conn.close()

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
