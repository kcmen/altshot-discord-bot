import discord
import sqlite3
import json
import csv
from discord import app_commands
from discord.ext import commands

ARCHIVE_CHANNEL_ID = 1360327905774801177

class AdminTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 🔐 Lock a week
    @app_commands.command(name="lock_week", description="Lock a specific week to prevent score changes.")
    @app_commands.describe(week="Week number to lock")
    async def lock_week(self, interaction: discord.Interaction, week: int):
        try:
            conn = sqlite3.connect("scores.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO locks (week, locked) VALUES (?, 1) ON CONFLICT(week) DO UPDATE SET locked = 1", (week,))
            conn.commit()
            conn.close()
            await interaction.response.send_message(f"🔐 Week {week} is now locked.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to lock Week {week}.\nError: `{str(e)}`", ephemeral=True)

    # 🗑️ Reset week scores
    @app_commands.command(name="reset_week", description="Delete all scores for a specific week.")
    @app_commands.describe(week="Week number to reset")
    async def reset_week(self, interaction: discord.Interaction, week: int):
        try:
            conn = sqlite3.connect("scores.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM scores WHERE week = ?", (week,))
            conn.commit()
            conn.close()
            await interaction.response.send_message(f"🗑️ All scores for **Week {week}** have been cleared.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to reset scores for Week {week}.\nError: `{str(e)}`", ephemeral=True)

    # 📬 Late reminder to all teams
    @app_commands.command(name="late_reminder", description="Remind all teams who haven’t submitted this week")
    @app_commands.describe(target="Use 'all' to ping all late teams.")
    async def late_reminder(self, interaction: discord.Interaction, target: str):
        if target != "all":
            await interaction.response.send_message("❌ Use `/late_reminder all` to ping all late teams.", ephemeral=True)
            return
        try:
            with open("teams.json", "r") as f:
                teams = json.load(f)
            conn = sqlite3.connect("scores.db")
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT week FROM scores ORDER BY week DESC LIMIT 1")
            current_week = cursor.fetchone()[0]
            submitted = set(row[0] for row in cursor.execute("SELECT team FROM scores WHERE week = ?", (current_week,)))
            conn.close()
            late_teams = [team for team in teams if team not in submitted]
            count = 0
            for team in late_teams:
                user_id = teams[team]
                user = interaction.guild.get_member(user_id)
                if user:
                    try:
                        await user.send(f"⏰ Hey {user.mention}, your team **{team}** hasn’t submitted your Week {current_week} score yet!")
                        count += 1
                    except Exception:
                        pass
            await interaction.response.send_message(f"✅ Reminders sent to {count} late team(s).", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to send reminders.\nError: `{str(e)}`", ephemeral=True)

    # 🧾 Archive scores to CSV and post to #lcs-archives
    @app_commands.command(name="archive_scores", description="Export all scores to archive.csv")
    async def archive_scores(self, interaction: discord.Interaction):
        try:
            conn = sqlite3.connect("scores.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scores")
            rows = cursor.fetchall()
            conn.close()
            with open("archive.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["team", "week", "opponent", "result", "holes_won"])
                writer.writerows(rows)

            archive_channel = interaction.guild.get_channel(ARCHIVE_CHANNEL_ID)
            if archive_channel:
                await archive_channel.send("📦 Season scores archive:", file=discord.File("archive.csv"))
                await interaction.response.send_message("✅ Archive posted to #lcs-archives.", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Archive channel not found.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to archive scores.\nError: `{str(e)}`", ephemeral=True)

    # 🛠️ Show admin help menu
    @app_commands.command(name="admin_help", description="View a list of admin commands and what they do")
    async def admin_help(self, interaction: discord.Interaction):
        msg = (
            "**🛠️ Admin Commands Overview**\n"
            "`/reset_week` — Delete all scores for a week\n"
            "`/lock_week` — Prevent score edits for a week\n"
            "`/unlock_week` — Allow score edits for a week\n"
            "`/late_reminder all` — DM all late teams\n"
            "`/archive_scores` — Export scores to CSV\n"
            "`/admin_help` — Show this menu\n"
            "`/start_season_guide` — Post the season guide to the designated channel"
        )
        await interaction.response.send_message(msg, ephemeral=True)

    # 📚 Start Season Guide Command
    @app_commands.command(name="start_season_guide", description="Post the season guide in the lcs-season-guide channel.")
    async def start_season_guide(self, interaction: discord.Interaction):
        channel = discord.utils.get(interaction.guild.text_channels, name="lcs-season-guide")
        if channel:
            season_guide_message = """
            **Welcome to the LCS Season Guide!** :trophy:

            Here is a helpful guide to get you started with the season:
            
            1. **Team Assignments**: Confirm your team roles in the `#teams` channel.
            2. **Match Schedule**: All match times and pairings will be posted in the `#match-schedule` channel.
            3. **Score Submission**: Scores must be submitted by 7:59 PM EST every Sunday. Use `/score` to submit.
            4. **Weekly Lock Deadline**: Matches will be locked at 8 PM EST, and no changes will be allowed after that time.
            5. **Week-to-Week Flow**: Each week's schedule and results will be posted in the `#mod-event` channel.

            Please ensure you're familiar with the information in the channels above.
            
            **Good luck and have fun!**
            """
            await channel.send(season_guide_message)
            await interaction.response.send_message("The season guide has been posted in the lcs-season-guide channel.", ephemeral=True)
        else:
            await interaction.response.send_message("The lcs-season-guide channel was not found. Please ensure the channel exists.", ephemeral=True)

# ✅ Only load the cog via bot.load_extension in bot.py
async def setup(bot):
    await bot.add_cog(AdminTools(bot))
