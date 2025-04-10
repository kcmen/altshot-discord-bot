import discord
import sqlite3
from discord import app_commands
from discord.ext import commands

class AdminTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 🔓 Unlock a week
    @app_commands.command(name="unlock_week", description="Unlock a specific week to allow score updates")
    @app_commands.describe(week="Week number to unlock")
    async def unlock_week(self, interaction: discord.Interaction, week: int):
        conn = sqlite3.connect("scores.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE locks SET locked = 0 WHERE week = ?", (week,))
        conn.commit()
        conn.close()
        await interaction.response.send_message(f"🔓 Week {week} is now unlocked.")

    # 🗑️ Reset week scores
    @app_commands.command(name="reset_week", description="Admin only: Delete all scores for a specific week.")
    @app_commands.checks.has_role("Admin")
    async def reset_week(self, interaction: discord.Interaction, week: int):
        try:
            conn = sqlite3.connect("scores.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM scores WHERE week = ?", (week,))
            conn.commit()
            conn.close()

            await interaction.response.send_message(
                f"🗑️ All scores for **Week {week}** have been cleared.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Failed to reset scores for Week {week}.\nError: `{str(e)}`",
                ephemeral=True
            )

# 🚀 Test auto-push with OBKoro1 1.0
    
async def setup(bot):
    await bot.add_cog(AdminTools(bot))
