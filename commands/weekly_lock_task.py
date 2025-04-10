import asyncio
from datetime import datetime, timedelta
import pytz
import discord
from discord.ext import commands, tasks

EASTERN = pytz.timezone("US/Eastern")
LOCK_CHANNEL_ID = 1229872678074093618  # Replace with your desired channel ID

class WeeklyLockTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_lock_deadline.start()

    def cog_unload(self):
        self.check_lock_deadline.cancel()

    @tasks.loop(minutes=5)
    async def check_lock_deadline(self):
        now = datetime.now(EASTERN)

        # Sunday at 7:59 PM EST
        if now.weekday() == 6 and now.hour == 19 and 55 <= now.minute <= 59:
            current_week = self.bot.week_tracker.get_current_week()
            if not self.bot.is_week_locked(current_week):
                self.bot.lock_week(current_week)
                channel = self.bot.get_channel(LOCK_CHANNEL_ID)
                if channel:
                    await channel.send(f"🔒 Week {current_week} has been auto-locked. All scores must now be final.")

    @check_lock_deadline.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(WeeklyLockTask(bot))
