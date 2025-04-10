import asyncio
import json
from datetime import datetime
import pytz
import discord
from discord.ext import commands, tasks

EASTERN = pytz.timezone("US/Eastern")
POST_CHANNEL_ID = 1229872678074093618  # Replace with your channel ID

class WeeklyMatchupPoster(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.post_matchups.start()

    def cog_unload(self):
        self.post_matchups.cancel()

    @tasks.loop(minutes=5)
    async def post_matchups(self):
        now = datetime.now(EASTERN)

        # Post matchups at 8:00 PM EST on Sunday
        if now.weekday() == 6 and now.hour == 20 and 0 <= now.minute <= 4:
            current_week = self.bot.week_tracker.get_current_week()
            try:
                with open("matchups.json", "r") as f:
                    data = json.load(f)

                matchups = data.get(str(current_week), [])
                if not matchups:
                    return

                post_channel = self.bot.get_channel(POST_CHANNEL_ID)
                if not post_channel:
                    return

                formatted = f"📣 **Alt Shot Matchups – Week {current_week}**\n\n"
                for match in matchups:
                    formatted += f"🆚 **{match['team1']}** vs **{match['team2']}**\n"

                await post_channel.send(formatted)

            except Exception as e:
                print(f"❌ Failed to auto-post matchups: {e}")

    @post_matchups.before_loop
    async def before_post_matchups(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(WeeklyMatchupPoster(bot))
