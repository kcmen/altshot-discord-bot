import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import json

class UnlockWeek(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="unlock_week", description="Unlock a specific week for score entry.")
    @app_commands.describe(week="Week number to unlock")
    async def unlock_week(self, interaction: discord.Interaction, week: int):
        try:
            # Unlock the week in the database
            conn = sqlite3.connect("scores.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO locks (week, locked) VALUES (?, 0)
                ON CONFLICT(week) DO UPDATE SET locked = 0
            """, (week,))
            conn.commit()
            conn.close()

            # Update the week_tracker.json file
            with open("week_tracker.json", "w") as f:
                json.dump({"current_week": week}, f)

            await interaction.response.send_message(
                f"✅ Week {week} has been unlocked and tracker updated.", ephemeral=True
            )

        except Exception as e:
            await interaction.response.send_message(
                f"❌ Failed to unlock week: `{str(e)}`", ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(UnlockWeek(bot))
