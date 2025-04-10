import discord
import sqlite3
from datetime import datetime
import pytz
from discord.ext import commands, tasks

EASTERN = pytz.timezone("US/Eastern")
RESULTS_CHANNEL_ID = 1229872734924011631  # Replace with your real results channel ID
HOLE_DIFF_CHANNEL_ID = 1229872783781009439  # Replace with your real hole diff channel ID

class WeeklyResultsPoster(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.post_results.start()

    def cog_unload(self):
        self.post_results.cancel()

    @tasks.loop(minutes=5)
    async def post_results(self):
        now = datetime.now(EASTERN)

        # Run at 8:15 PM EST Sunday
        if now.weekday() == 6 and now.hour == 20 and 15 <= now.minute <= 19:
            current_week = self.bot.week_tracker.get_current_week()

            results_channel = self.bot.get_channel(RESULTS_CHANNEL_ID)
            hole_diff_channel = self.bot.get_channel(HOLE_DIFF_CHANNEL_ID)
            if not results_channel or not hole_diff_channel:
                return

            try:
                # Load and post results
                conn = sqlite3.connect("scores.db")
                cursor = conn.cursor()
                cursor.execute("SELECT team1, team2, result, holes_won FROM scores WHERE week = ?", (current_week,))
                matches = cursor.fetchall()

                if not matches:
                    await results_channel.send(f"⚠️ No match results found for Week {current_week}.")
                    return

                results_msg = f"📋 **Week {current_week} Results**\n\n"
                hole_diff = {}

                for match in matches:
                    t1, t2, result, holes = match
                    results_msg += f"🏌️‍♂️ {t1} vs {t2} → **{result}** ({holes} holes won)\n"

                    winner = result if result in (t1, t2) else None
                    if winner:
                        hole_diff[winner] = hole_diff.get(winner, 0) + holes

                await results_channel.send(results_msg)

                # Post hole diff leaderboard
                leaderboard = sorted(hole_diff.items(), key=lambda x: x[1], reverse=True)
                hole_msg = f"📊 **Hole Differential Standings (Week {current_week})**\n\n"
                for rank, (team, total) in enumerate(leaderboard, 1):
                    hole_msg += f"{rank}. **{team}** — {total} holes\n"

                await hole_diff_channel.send(hole_msg)

            except Exception as e:
                await results_channel.send(f"❌ Error posting results: `{str(e)}`")

    @post_results.before_loop
    async def before_post_results(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(WeeklyResultsPoster(bot))
