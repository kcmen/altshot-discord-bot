import json
import discord
from discord import app_commands
from discord.ext import commands
from utils.week_tracker import get_current_week

class DynamicSchedule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="schedule", description="View weekly Alt Shot matchups from schedule.json")
    @app_commands.describe(week="Optional week number to view (defaults to current week)")
    async def schedule(self, interaction: discord.Interaction, week: int = None):
        try:
            with open("schedule.json", "r") as f:
                data = json.load(f)

            if not week:
                week = get_current_week()

            week_key = f"Week {week}"
            matchups = data.get(week_key)

            if not matchups:
                await interaction.response.send_message(f"❌ No matchups found for Week {week}.", ephemeral=True)
                return

            msg = f"📅 **Matchups for Week {week}**\n\n"
            for match in matchups:
                msg += f"🆚 **{match['team1']}** vs **{match['team2']}**\n"

            await interaction.response.send_message(msg)

        except Exception as e:
            await interaction.response.send_message(f"❌ Error loading schedule: `{str(e)}`", ephemeral=True)

async def setup(bot):
    await bot.add_cog(DynamicSchedule(bot))
