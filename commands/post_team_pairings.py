import os
import json
import discord
from discord.ext import commands
from discord import app_commands

PAIRINGS_CHANNEL_ID = 1356650434340720690  # #team-pairings
PAIRINGS_FLAG_FILE = "pairings_posted.flag"

class PostTeamPairings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.delayed_post_team_pairings())  # Run after full bot ready

    async def delayed_post_team_pairings(self):
        await self.bot.wait_until_ready()
        if os.path.exists(PAIRINGS_FLAG_FILE):
            print("🟡 Team pairings already posted (flag detected). Skipping...")
            return
        await self.post_team_pairings()

    async def post_team_pairings(self):
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
                with open(PAIRINGS_FLAG_FILE, "w") as flag:
                    flag.write("posted")
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

async def setup(bot):
    await bot.add_cog(PostTeamPairings(bot))

