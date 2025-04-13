import pytz
from datetime import datetime
import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os

LOCK_CHANNEL_ID = 1356054216728252506  # #matchup-schedule
EASTERN = pytz.timezone("US/Eastern")

class WeeklyMatchupPoster(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auto_lock.start()
        self.week_change_monitor.start()

    def cog_unload(self):
        self.auto_lock.cancel()
        self.week_change_monitor.cancel()

    # 🔁 Scheduled weekly lock (Sunday 6:59 PM EST)
    @tasks.loop(minutes=1)
    async def auto_lock(self):
        now = datetime.now(EASTERN)
        if now.weekday() == 6 and now.hour == 18 and now.minute == 59:
            await self.post_week_matchups(lock_week=True)

    # 🔁 Detect unlocked week + missing flag = post matchups
    @tasks.loop(seconds=15)
    async def week_change_monitor(self):
        if not os.path.exists("week_tracker.json") or os.path.exists("pairings_posted.flag"):
            return

        with open("week_tracker.json", "r") as f:
            data = json.load(f)
            current_week = data.get("current_week", 1)

        week_key = f"Week {current_week}"

        # Load schedule to check if matchups exist
        with open("schedule.json", "r") as sf:
            schedule = json.load(sf)

        if week_key not in schedule:
            return  # Nothing to post

        await self.post_week_matchups(lock_week=False)

        # Set flag so it doesn't post again until week is advanced
        with open("pairings_posted.flag", "w") as flag:
            flag.write(f"Posted matchups for {week_key}")

    @app_commands.command(name="post_week_matchups", description="Manually post matchups without locking the week")
    async def post_week_matchups_command(self, interaction: discord.Interaction):
        try:
            await self.post_week_matchups(lock_week=False)
            await interaction.response.send_message("📬 Matchups posted manually (no lock).", ephemeral=True)
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Failed to post matchups: `{str(e)}`", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ Failed to post matchups: `{str(e)}`", ephemeral=True)

    async def post_week_matchups(self, lock_week=False):
        with open("schedule.json", "r") as sf:
            schedule = json.load(sf)
        with open("week_tracker.json", "r") as wf:
            current_week = json.load(wf).get("current_week", 1)

        week_key = f"Week {current_week}"
        if lock_week:
            self.bot.lock_week(current_week)

        channel = self.bot.get_channel(LOCK_CHANNEL_ID)
        if channel:
            try:
                with open("teams.json", "r") as tf:
                    teams = json.load(tf)

                matchups = schedule.get(week_key, [])
                lines = []
                for match in matchups:
                    team1 = match["team1"]
                    team2 = match["team2"]
                    team1_players = " / ".join(teams.get(team1, {}).get("players", ["Unknown"]))
                    team2_players = " / ".join(teams.get(team2, {}).get("players", ["Unknown"]))
                    lines.append(f"🔹 {team1} 🆚 {team2}\n👥 {team1_players} vs {team2_players}")

                message = (
                    f"### 🌟 **LIVE NOW: Alt Shot Circuit – {week_key} Matchups** 🌟\n"
                    f"🎯 Rally your duo and lock in!\nIt’s time to swing big, putt smooth, and play like champs.\n\n"
                    + "\n".join(lines) +
                    "\n\n📅 **Match Deadline:** Sunday @ 6:59 PM EST\n"
                    "📝 Don't forget to submit your scorecard in <#1356478618703892541>\n"
                    "🔥 GLHF out there, legends!"
                )
                await channel.send(message)

                if lock_week:
                    await channel.send(
                        f"🔒 **{week_key} has been automatically locked!**  \n"
                        f"📅 Deadline has passed — 🛑 No further score submissions or edits are allowed  \n"
                        f"✅ Only admins may approve changes under special circumstances."
                    )

            except Exception as e:
                await channel.send(f"⚠️ Failed to load matchups: {e}")

    @auto_lock.before_loop
    @week_change_monitor.before_loop
    async def before_tasks(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(WeeklyMatchupPoster(bot))
