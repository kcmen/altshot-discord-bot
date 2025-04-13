import discord
import json
from discord.ext import commands
from discord import app_commands

class ViewTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="current_week", description="View the current week from tracker file")
    async def current_week(self, interaction: discord.Interaction):
        try:
            with open("week_tracker.json", "r") as f:
                week = json.load(f).get("current_week", "unknown")
            await interaction.response.send_message(
                f"📅 Railway says current week is: **Week {week}**",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error reading week_tracker.json: `{str(e)}`",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(ViewTracker(bot))
