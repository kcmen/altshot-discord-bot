import json
import discord
from discord.ext import commands
from discord import app_commands

PAIRINGS_CHANNEL_ID = 1356650434340720690  # #team-pairings

class PostTeamPairings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.has_posted_pairings = False  # Prevent reposting every restart

    async def post_team_pairings(self):
        if self.has_posted_pairings:
            return

        try:
            with open("teams.json", "r") as f:
                teams = json.load(f)

            lines = ["📋 **LCS Alt Shot Team Pairings**\n"]
            for team, data in teams.items():
                players = " / ".join(data.get("players", []))
                lines.append(f"{team}: {players}")

            message = "\n".join(lines)
            channel = self.bot.get_channel(PAIRINGS_CHANNEL_ID)
            if channel:
                await channel.send(message)
                self.has_posted_pairings = True
                print("✅ Team pairings posted.")

        except Exception as e:
            print(f"❌ Failed to post team pairings: {e}")

    @app_commands.command(name="post_team_pairings", description="Manually post the team pairings list")
    async def post_team_pairings_command(self, interaction: discord.Interaction):
        try:
            await self.post_team_pairings()
            await interaction.response.send_message("📬 Team pairings have been posted.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to post team pairings: `{str(e)}`", ephemeral=True)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.post_team_pairings()  # Post once on first startup

async def setup(bot):
    await bot.add_cog(PostTeamPairings(bot))
