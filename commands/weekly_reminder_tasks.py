import discord
from discord.ext import tasks, commands
from datetime import datetime, timedelta
import pytz
import sqlite3
from utils.team_name_loader import get_team_name
from utils.week_tracker import get_current_week

REAL_USER_IDS = {
    "T1": 1345822059061575792,  # HunkerDownHound
    "T2": 319573965234241538,   # CoachPengy
    "T3": 513413846623453237,   # Stikkydixx
    "T4": 1338790280664453163,  # xWopmz
}

class WeeklyReminderTasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reminder_check.start()

    def cog_unload(self):
        self.reminder_check.cancel()

    @tasks.loop(minutes=1)
    async def reminder_check(self):
        est = pytz.timezone("US/Eastern")
        now = datetime.now(tz=est)
        weekday = now.weekday()
        hour = now.hour
        minute = now.minute

        # Determine the correct message type based on schedule
        if (weekday == 4 and hour == 20 and minute == 0) or \
           (weekday == 5 and hour == 20 and minute == 0) or \
           (weekday == 6 and hour == 14 and minute == 0):

            # Determine how many hours left (for Sunday message)
            hours_remaining = 5 if weekday == 6 else None
            await self.send_reminders(hours_remaining)

    async def send_reminders(self, hours_remaining=None):
        current_week = get_current_week()

        # Connect to scores DB
        conn = sqlite3.connect("scores.db")
        cursor = conn.cursor()

        # Get list of teams with scores already submitted this week
        cursor.execute("SELECT team FROM scores WHERE week = ?", (current_week,))
        submitted_teams = set(row[0] for row in cursor.fetchall())

        # All 20 teams
        all_teams = [f"T{i}" for i in range(1, 21)]

        # Identify teams that haven't submitted yet
        pending_teams = [team for team in all_teams if team not in submitted_teams]

        for team in pending_teams:
            user_id = REAL_USER_IDS.get(team)
            if user_id:
                try:
                    user = await self.bot.fetch_user(user_id)
                    if user:
                        team_name = get_team_name(team)
                        message = f"⏰ Reminder: Your team **{team_name} ({team})** still hasn't submitted a score for Week {current_week}."
                        if hours_remaining is not None:
                            message += f"\n⏳ You have **{hours_remaining} hours** remaining before this event closes."
                        await user.send(message)
                except Exception as e:
                    print(f"❌ Failed to DM user for team {team}: {e}")

        conn.close()

async def setup(bot):
    await bot.add_cog(WeeklyReminderTasks(bot))
