import discord
import sqlite3
import json
from discord.ext import commands
from discord import app_commands

class ReminderCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="reminder", description="Send a reminder to a specific user.")
    @app_commands.describe(user="User to remind", week="Week number (optional)")
    async def send_reminder(self, interaction: discord.Interaction, user: discord.User, week: int = None):
        try:
            if week:
                message = f"👋 Friendly reminder: Please report your score for Week {week}."
            else:
                message = "👋 Friendly reminder: Please report your score."

            await user.send(message)
            await interaction.response.send_message(f"✅ Reminder sent to {user.mention}.", ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to send reminder: {e}", ephemeral=True)

    @app_commands.command(name="late_reminder", description="Admin only: DM all teams who haven't submitted scores this week.")
    @app_commands.describe(week="Week number to check")
    @app_commands.checks.has_role("Admin")
    async def late_reminder_all(self, interaction: discord.Interaction, week: int):
        try:
            with open("teams.json", "r") as f:
                teams = json.load(f)

            conn = sqlite3.connect("scores.db")
            cursor = conn.cursor()

            missing_teams = []
            for team_code, team_info in teams.items():
                cursor.execute("SELECT * FROM scores WHERE team = ? AND week = ?", (team_code, week))
                if not cursor.fetchone():
                    missing_teams.append((team_code, team_info["players"]))

            conn.close()

            for team_code, players in missing_teams:
                for user_id in players:
                    try:
                        user = await interaction.client.fetch_user(user_id)
                        await user.send(f"👋 Friendly reminder: Team **{team_code}** hasn't submitted a score for Week {week} yet. Please report ASAP!")
                    except Exception as e:
                        print(f"⚠️ Could not send DM to {user_id}: {e}")

            await interaction.response.send_message(
                f"📨 Sent reminders to {len(missing_teams)} team(s) for Week {week}.",
                ephemeral=True
            )

        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error sending late reminders: `{str(e)}`",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(ReminderCommands(bot))
