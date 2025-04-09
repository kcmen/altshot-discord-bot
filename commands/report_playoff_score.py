import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
from generate_playoff_bracket import ROUND_MAP, VALID_MATCHES
from utils.team_name_loader import get_team_name

class ReportPlayoffScore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="report_playoff_score", description="Enter a playoff match result and update bracket.")
    @app_commands.describe(
        round="Playoff round (Q, S, F or full name)",
        match="Match number (1, 2, etc.)",
        team1="First team code (e.g., T7)",
        team2="Second team code (e.g., T12)",
        winner="Winning team code (must be T7 or T12)"
    )
    async def report_playoff_score(
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
        if not valid_matches or match not in valid_matches:
            await interaction.response.send_message(f"❌ Invalid match number for {round_name}.", ephemeral=True)
            return

        team1 = team1.upper().strip()
        team2 = team2.upper().strip()
        winner = winner.upper().strip()

        if winner not in [team1, team2]:
            await interaction.response.send_message("❌ Winner must be one of the two teams in the match.", ephemeral=True)
            return

        conn = sqlite3.connect("scores.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS playoff_scores (
                round TEXT,
                match INTEGER,
                team1 TEXT,
                team2 TEXT,
                winner TEXT,
                PRIMARY KEY (round, match)
            )
        """)

        # Check for duplicate entry
        cursor.execute("""
            SELECT * FROM playoff_scores
            WHERE round = ? AND match = ?
        """, (round_name, match))
        if cursor.fetchone():
            await interaction.response.send_message("⚠️ A score already exists for this match. Use /delete_playoff_score first if needed.", ephemeral=True)
            conn.close()
            return

        cursor.execute("""
            INSERT INTO playoff_scores (round, match, team1, team2, winner)
            VALUES (?, ?, ?, ?, ?)
        """, (round_name, match, team1, team2, winner))
        conn.commit()
        conn.close()

        await interaction.response.send_message(
            f"✅ Playoff result recorded: {get_team_name(winner)} ({winner}) won {round_name} Match {match}.",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(ReportPlayoffScore(bot))
