import json
import discord
from discord import app_commands
from discord.ext import commands

class WeeklyPostMatchups(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="post_week_matchups",
        description="Manually post weekly matchups and auto-lock the week"
    )
    @app_commands.describe(week="Week number to post matchups for")
    async def post_week_matchups(self, interaction: discord.Interaction, week: int):
        try:
            with open("schedule.json", "r") as f:
                schedule = json.load(f)
            with open("teams.json", "r") as tf:
                teams = json.load(tf)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to load data: {e}", ephemeral=True)
            return

        week_key = f"Week {week}"
        if week_key not in schedule:
            await interaction.response.send_message(f"⚠️ No schedule found for {week_key}", ephemeral=True)
            return

        msg = f"**📅 WEEK {week} MATCHUPS**\n\n"
        for team1, team2 in schedule[week_key]:
            team1_names = " / ".join(teams.get(team1, {}).get("players", [team1]))
            team2_names = " / ".join(teams.get(team2, {}).get("players", [team2]))
            msg += f"🔹 **{team1} vs {team2}** — {team1_names} vs {team2_names}\n"

        # Post matchups and lock confirmation
        await interaction.response.send_message(msg)
        self.bot.lock_week(week)
        await interaction.followup.send(f"🔒 Week {week} has been automatically locked!")

async def setup(bot):
    await bot.add_cog(WeeklyPostMatchups(bot))
