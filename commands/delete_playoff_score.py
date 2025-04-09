import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
from generate_playoff_bracket import ROUND_MAP, VALID_MATCHES

class DeletePlayoffScore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="delete_playoff_score", description="Delete a specific playoff match result.")
    @app_commands.describe(
        round="Playoff round (Q, S, F or full name)",
        match="Match number to delete (e.g., 1, 2)"
    )
    async def delete_playoff_score(self, interaction: discord.Interaction, round: str, match: int):
        round_key = round.strip().lower()
        round_name = ROUND_MAP.get(round_key)

        if not round_name:
            await interaction.response.send_message("❌ Invalid round. Use Q, S, F or full round names.", ephemeral=True)
            return

        valid_matches = VALID_MATCHES.get(round_name)
        if match not in valid_matches:
            await interaction.response.send_message(f"❌ Invalid match number for {round_name}.", ephemeral=True)
            return

        conn = sqlite3.connect("scores.db")
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM playoff_scores
            WHERE round = ? AND match = ?
        """, (round_name, match))
        conn.commit()
        conn.close()

        await interaction.response.send_message(f"🗑️ Deleted {round_name} Match {match}.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(DeletePlayoffScore(bot))
