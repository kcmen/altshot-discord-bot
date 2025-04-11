import pytz
from datetime import datetime
import discord
from discord.ext import commands, tasks

LOCK_CHANNEL_ID = 1356054216728252506  # #matchup-schedule
EASTERN = pytz.timezone("US/Eastern")

class WeeklyLocker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auto_lock.start()

    def cog_unload(self):
        self.auto_lock.cancel()

    @tasks.loop(minutes=1)
    async def auto_lock(self):
        now = datetime.now(EASTERN)
        if now.weekday() == 6 and now.hour == 19 and 59 <= now.minute <= 59:
            current_week = self.bot.week_tracker.get_current_week()
            self.bot.lock_week(current_week)

            channel = self.bot.get_channel(LOCK_CHANNEL_ID)
            if channel:
                await channel.send(
                    f"🔒 **Week {current_week} has been automatically locked!**  \n"
                    f"📅 Deadline has passed — 🛑 No further score submissions or edits are allowed  \n"
                    f"✅ Only admins may approve changes under special circumstances."
                )

    @auto_lock.before_loop
    async def before_auto_lock(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(WeeklyLocker(bot))
