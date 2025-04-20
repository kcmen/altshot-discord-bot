import discord
from discord import app_commands
from discord.ext import commands
import sqlite3

class ResetPlayoffs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="reset_playoffs", description="Clear all playoff scores and matchups.")
    async def reset_playoffs(self, interaction: discord.Interaction):
        conn = sqlite3.connect("scores.db")
        cursor = conn.cursor()

        messages = []

        def safe_delete(table):
            try:
                cursor.execute(f"DELETE FROM {table};")
                messages.append(f"✅ Cleared: `{table}`")
            except sqlite3.OperationalError as e:
                messages.append(f"⚠️ Skipped `{table}`: {e}")

        safe_delete("playoff_scores")
        safe_delete("playoff_matchups")

        conn.commit()
        conn.close()

        response = "\n".join(messages) + "\n\n🏁 Playoffs have been reset."
        await interaction.response.send_message(response, ephemeral=True)

async def setup(bot):
    await bot.add_cog(ResetPlayoffs(bot))
