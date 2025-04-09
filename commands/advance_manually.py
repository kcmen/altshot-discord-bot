import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
from generate_playoff_bracket import ROUND_MAP, VALID_MATCHES

class AdvancePlayoffManually(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="advance_manually", description="Manually insert a playoff winner into the bracket.")
    @app_commands.describe(
        round="Playoff round (Q, S, F or full name)",
        match="Match number (1, 2, 3, or 4)",
        team1="Team 1 (e.g., T3)",
        team2="Team 2 (e.g., T7)",
        winner="Winning team code (e.g., T3)"
    )
    async def advance_manually(
        self,
        interaction: discord.Interaction,
        round: str,
        match: int,
        team1: str,
        team2: str,
        winner: str
    ):
        round_key = round.strip().lower()
        round_name = ROUND_MAP.get(round_key)

        if not round_name:
            await interaction.response.send_message("❌ Invalid round. Use Q, S, F or full round names.", ephemeral=True)
            return

        valid_matches = VALID_MATCHES.get(round_name)
        if match not in valid_matches:
            await interaction.response.send_message(f"❌ Invalid match number for {round_name}.", ephemeral=True)
            return

        winner = winner.upper()
        team1 = team1.upper()
        team2 = team2.upper()

        conn = sqlite3.connect("scores.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO playoff_scores (round, match, team1, team2, winner)
            VALUES (?, ?, ?, ?, ?)
        """, (round_name, match, team1, team2, winner))
        conn.commit()
        conn.close()

        await interaction.response.send_message(
            f"✅ {round_name} Match {match} manually updated.\n**Winner:** {winner}", ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(AdvancePlayoffManually(bot))
