import os
import json
import sqlite3
import discord
from discord.ext import commands
from discord import app_commands

PAIRINGS_CHANNEL_ID = 1360831176897597550  # #team-pairings (updated)
MATCHUP_CHANNEL_ID = 1356054216728252506  # #matchup-schedule

class PostTeamPairings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.delayed_post_team_pairings())

    async def delayed_post_team_pairings(self):
        await self.bot.wait_until_ready()
        if self.has_posted_flag("pairings_posted"):
            print("🟡 Team pairings already posted (flag detected). Skipping...")
            return
        await self.post_team_pairings()

    def has_posted_flag(self, flag_name):
        conn = sqlite3.connect("scores.db")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS flags (name TEXT PRIMARY KEY)")
        cursor.execute("SELECT name FROM flags WHERE name = ?", (flag_name,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def mark_flag_posted(self, flag_name):
        conn = sqlite3.connect("scores.db")
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO flags (name) VALUES (?)", (flag_name,))
        conn.commit()
        conn.close()

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
                self.mark_flag_posted("pairings_posted")
                print("✅ Team pairings posted.")

            # 🔁 If week is 1 and matchups not posted yet, auto-post week 1 matchups
            if not self.has_posted_flag("week_1_posted"):
                await self.auto_post_week_1_matchups(teams)

        except Exception as e:
            print(f"❌ Failed to post team pairings: {e}")

    async def auto_post_week_1_matchups(self, teams):
        try:
            with open("schedule.json", "r") as f:
                schedule = json.load(f)
            week_1_matches = schedule.get("Week 1", [])
            if not week_1_matches:
                print("⚠️ No Week 1 matchups found in schedule.json.")
                return

            lines = ["### 🌟 **LIVE NOW: Alt Shot Circuit – Week 1 Matchups** 🌟",
                     "🎯 Rally your duo and lock in!",
                     "It’s time to swing big, putt smooth, and play like champs.\n"]

            for match in week_1_matches:
                t1, t2 = match["team1"], match["team2"]
                p1 = " / ".join(teams.get(t1, {}).get("players", []))
                p2 = " / ".join(teams.get(t2, {}).get("players", []))
                lines.append(f"🔹 {t1} 🆚 {t2}")
                lines.append(f"👥 {p1} vs {p2}")

            lines.append("\n📅 **Match Deadline:** Sunday @ 6:59 PM EST")
            lines.append("📝 Don't forget to submit your scorecard in <#1356478618703892541>")
            lines.append("🔥 GLHF out there, legends!")

            matchup_channel = self.bot.get_channel(MATCHUP_CHANNEL_ID)
            if matchup_channel:
                await matchup_channel.send("\n".join(lines))
                self.mark_flag_posted("week_1_posted")
                print("✅ Week 1 matchups auto-posted.")

        except Exception as e:
            print(f"❌ Failed to auto-post Week 1 matchups: {e}")

    @app_commands.command(name="post_team_pairings", description="Manually post the team pairings list")
    async def post_team_pairings_command(self, interaction: discord.Interaction):
        try:
            await self.post_team_pairings()
            await interaction.response.send_message("📬 Team pairings have been posted.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to post team pairings: `{str(e)}`", ephemeral=True)

async def setup(bot):
    await bot.add_cog(PostTeamPairings(bot))
