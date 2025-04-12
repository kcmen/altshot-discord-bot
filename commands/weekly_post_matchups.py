import pytz
from datetime import datetime
import discord
from discord.ext import commands, tasks
from discord import app_commands
import json

LOCK_CHANNEL_ID = 1356054216728252506  # #matchup-schedule
EASTERN = pytz.timezone("US/Eastern")

class WeeklyMatchupPoster(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auto_lock.start()

    def cog_unload(self):
        self.auto_lock.cancel()

    @tasks.loop(minutes=1)
    async def auto_lock(self):
        now = datetime.now(EASTERN)
        if now.weekday() == 6 and now.hour == 19 and 59 <= now.minute <= 59:
            await self.post_week_matchups()

    @app_commands.command(name="post_week_matchups", description="Manually post matchups and lock the week")
    async def post_week_matchups(self, interaction: discord.Interaction):
        await self.post_week_matchups()
        await interaction.response.send_message("📬 Matchups posted and week locked manually.", ephemeral=True)

    async def post_week_matchups(self):
        current_week = self.bot.week_tracker.get_current_week()
        self.bot.lock_week(current_week)

        channel = self.bot.get_channel(LOCK_CHANNEL_ID)
        if channel:
            try:
                try:
                    with open("teams.json", "r") as tf:
                        teams = json.load(tf)
                except Exception as e:
                    print(f"❌ Failed to load teams.json: {e}")
                    teams = {}

                with open("schedule.json", "r") as sf:
                    schedule = json.load(sf)
                matchups = schedule.get(str(current_week), [])

                lines = []
                for team1, team2 in matchups:
                    t1_data = teams.get(team1, {})
                    t2_data = teams.get(team2, {})
                    t1_players = " / ".join(t1_data.get("players", [team1]))
                    t2_players = " / ".join(t2_data.get("players", [team2]))
                    lines.append(f"{team1} 🆚 {team2}\n👥 {t1_players} vs {t2_players}")

                message = (
                    f"### 💫 **LIVE NOW: Alt Shot Circuit – Week {current_week} Matchups** 💫\n\n"
                    f"🎯 **Rally your duo and lock in!**\nIt’s time to swing big, putt smooth, and play like champs.\n\n"
                    + "\n".join(lines) + "\n\n"
                    "📅 **Match Deadline:** Sunday @ 6:59 PM EST\n"
                    "📝 Don't forget to submit your scorecard in <#1341714428592132136>\n"
                    "🔥 GLHF out there, legends!"
                )
                await channel.send(message)
            except Exception as e:
                await channel.send(f"⚠️ Failed to load matchups: {e}")

            await channel.send(
                f"🔒 **Week {current_week} has been automatically locked!**  \n"
                f"📅 Deadline has passed — 🛑 No further score submissions or edits are allowed  \n"
                f"✅ Only admins may approve changes under special circumstances."
            )

    @auto_lock.before_loop
    async def before_auto_lock(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(WeeklyMatchupPoster(bot))
