import discord
import json
import os
from discord.ext import commands

TEAM_PAIRINGS_CHANNEL_ID = 1356650434340720690

class TeamPairings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def post_team_pairings(self, guild):
        if not os.path.exists("teams.json"):
            print("teams.json not found. Skipping team pairings post.")
            return

        try:
            with open("teams.json", "r") as f:
                teams = json.load(f)

            lines = ["📋 **LCS Alt Shot Team Pairings**\n"]
            for team, data in teams.items():
                players = data.get("players", [])
                lines.append(f"{team}: {' / '.join(players)}")

            content = "\n".join(lines)
            channel = guild.get_channel(TEAM_PAIRINGS_CHANNEL_ID)
            if channel:
                await channel.send(content)
                print("✅ Team pairings posted.")
            else:
                print("❌ Could not find #team-pairings channel.")
        except Exception as e:
            print(f"❌ Failed to post team pairings: {e}")

async def setup(bot):
    cog = TeamPairings(bot)
    await bot.add_cog(cog)

    # Trigger post after load if bot is ready
    if bot.is_ready():
        await cog.post_team_pairings(bot.get_guild(bot.guilds[0].id))
    else:
        @bot.event
        async def on_ready():
            await cog.post_team_pairings(bot.get_guild(bot.guilds[0].id))
