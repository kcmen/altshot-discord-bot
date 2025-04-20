import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
from generate_playoff_bracket import ROUND_MAP, VALID_MATCHES

class ViewPlayoffScore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="view_playoff_score", description="View reported playoff scores by round or match.")
    @app_commands.describe(
        round="Playoff round (Q, S, F or full name)",
        match="(Optional) Match number to view (1, 2, etc.)"
    )
    async def view_playoff_score(self, interaction: discord.Interaction, round: str, match: int = None):
        round_key = round.strip().lower()
        round_name = ROUND_MAP.get(round_key)

        if not round_name:
            await interaction.response.send_message("❌ Invalid round. Use Q, S, F or full round names.", ephemeral=True)
            return

        valid_matches = VALID_MATCHES.get(round_name)
        if match and (match not in valid_matches):
            await interaction.response.send_message(f"❌ Invalid match number for {round_name}.", ephemeral=True)
            return

        conn = sqlite3.connect("scores.db")
        cursor = conn.cursor()

        if match:
            cursor.execute("""
                SELECT match, team1, team2, winner
                FROM playoff_scores
                WHERE round = ? AND match = ?
            """, (round_name, match))
        else:
            cursor.execute("""
                SELECT match, team1, team2, winner
                FROM playoff_scores
                WHERE round = ?
                ORDER BY match
            """, (round_name,))

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            await interaction.response.send_message(f"❌ No scores found for {round_name}.", ephemeral=True)
            return

        lines = [f"📋 **{round_name} Results**\n"]
        for m, t1, t2, w in rows:
            lines.append(f"Match {m}: {t1} vs {t2} → Winner: {w}")

        await interaction.response.send_message("\n".join(lines), ephemeral=True)

async def setup(bot):
    await bot.add_cog(ViewPlayoffScore(bot))
