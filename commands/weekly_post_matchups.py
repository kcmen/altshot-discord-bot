import json
import discord
from discord import app_commands
from discord.ext import commands

class WeeklyMatchups(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="post_week_matchups", description="Post matchups for a specific week and lock it")
    @app_commands.describe(week="The week number to post")
    async def post_week_matchups(self, interaction: discord.Interaction, week: int):
        try:
            with open("schedule.json", "r") as sf:
                schedule = json.load(sf)
            with open("teams.json", "r") as tf:
                teams = json.load(tf)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to load files: {e}", ephemeral=True)
            return

        week_key = f"Week {week}"
        matchups = schedule.get(week_key)
        if not matchups:
            await interaction.response.send_message(f"⚠️ No matchups found for Week {week}", ephemeral=True)
            return

        message = f"🌟 **LIVE NOW: Alt Shot Circuit – Week {week} Matchups** 🌟\n"
        message += "🎯 **Rally your duo and lock in!**\nIt’s time to swing big, putt smooth, and play like champs.\n\n"

        for team1, team2 in matchups:
            t1_names = " / ".join(teams.get(team1, {}).get("players", [team1]))
            t2_names = " / ".join(teams.get(team2, {}).get("players", [team2]))
            message += f"🔹 **{team1} vs {team2}** — {t1_names} vs {t2_names}\n"

        await interaction.response.send_message(message)

        # Lock the week in database
        self.bot.lock_week(week)
        await interaction.followup.send(
            f"🔒 **Week {week} has been automatically locked!**\n"
            f"📅 Deadline has passed — 🛑 No further score submissions or edits are allowed\n"
            f"✅ Only admins may approve changes under special circumstances."
        )

async def setup(bot):
    await bot.add_cog(WeeklyMatchups(bot))
