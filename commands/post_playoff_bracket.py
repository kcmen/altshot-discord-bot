# commands/post_playoff_bracket.py
import discord
from discord import app_commands
from discord.ext import commands
from generate_playoff_bracket import generate_quarterfinals, generate_semifinals_from_scores, generate_finals_from_scores
from utils.team_name_loader import get_team_name

PLAYOFF_CHANNEL_ID = 1359236509131079933  # Replace with your actual playoff channel ID

class PostPlayoffBracket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="post_quarterfinals", description="Post the Alt Shot Circuit quarterfinal playoff bracket.")
    async def post_quarterfinals(self, interaction: discord.Interaction):
        bracket = generate_quarterfinals()

        if not bracket:
            await interaction.response.send_message("❌ Could not generate quarterfinal bracket.", ephemeral=True)
            return

        lines = []
        for idx, (team1, team2) in enumerate(bracket, 1):
            name1 = get_team_name(team1)
            name2 = get_team_name(team2)
            lines.append(f"**QF{idx}:** {name1} ({team1}) 🆚 {name2} ({team2})")

        message = "🏆 **Alt Shot Circuit Playoffs – Quarterfinals**\n\n" + "\n".join(lines)
        await self._send_playoff_announcement(interaction, message)

    @app_commands.command(name="post_semifinals", description="Post the semifinal matchups.")
    async def post_semifinals(self, interaction: discord.Interaction):
        bracket = generate_semifinals_from_scores()

        if not bracket:
            await interaction.response.send_message("❌ Could not generate semifinal bracket from scores.", ephemeral=True)
            return

        lines = []
        for idx, (team1, team2) in enumerate(bracket, 1):
            name1 = get_team_name(team1)
            name2 = get_team_name(team2)
            lines.append(f"**SF{idx}:** {name1} ({team1}) 🆚 {name2} ({team2})")

        message = "🏆 **Alt Shot Circuit Playoffs – Semifinals**\n\n" + "\n".join(lines)
        await self._send_playoff_announcement(interaction, message)

    @app_commands.command(name="post_finals", description="Post the championship and 3rd place matches.")
    async def post_finals(self, interaction: discord.Interaction):
        finals = generate_finals_from_scores()

        if not finals:
            await interaction.response.send_message("❌ Could not generate finals from scores.", ephemeral=True)
            return

        champ1, champ2 = finals["Championship"]
        third1, third2 = finals["Third Place"]

        message = (
            "🏆 **Alt Shot Circuit Playoffs – Finals**\n\n"
            f"🥇 **Championship Match:** {get_team_name(champ1)} ({champ1}) 🆚 {get_team_name(champ2)} ({champ2})\n"
            f"🥉 **3rd Place Match:** {get_team_name(third1)} ({third1}) 🆚 {get_team_name(third2)} ({third2})"
        )

        await self._send_playoff_announcement(interaction, message)

    async def _send_playoff_announcement(self, interaction, message):
        channel = self.bot.get_channel(PLAYOFF_CHANNEL_ID)
        if channel:
            await channel.send(message)
            await interaction.response.send_message("✅ Playoff bracket posted!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Could not find playoff channel.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(PostPlayoffBracket(bot))
