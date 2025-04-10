import discord
import sqlite3
import json
import csv
from discord import app_commands
from discord.ext import commands

class AdminTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 🔓 Unlock a week
    @app_commands.command(name="unlock_week", description="Unlock a specific week to allow score updates")
    @app_commands.describe(week="Week number to unlock")
    async def unlock_week(self, interaction: discord.Interaction, week: int):
        conn = sqlite3.connect("scores.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE locks SET locked = 0 WHERE week = ?", (week,))
        conn.commit()
        conn.close()
        await interaction.response.send_message(f"🔓 Week {week} is now unlocked.")

    # 🔐 Lock a week
    @app_commands.command(name="lock_week", description="Admin only: Lock a specific week to prevent score changes.")
    @app_commands.describe(week="Week number to lock")
    @app_commands.checks.has_role("Admin")
    async def lock_week(self, interaction: discord.Interaction, week: int):
        try:
            conn = sqlite3.connect("scores.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO locks (week, locked) VALUES (?, 1) ON CONFLICT(week) DO UPDATE SET locked = 1", (week,))
            conn.commit()
            conn.close()
            await interaction.response.send_message(f"🔒 Week {week} is now locked.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to lock Week {week}.\nError: `{str(e)}`", ephemeral=True)

    # 🗑️ Reset week scores
    @app_commands.command(name="reset_week", description="Admin only: Delete all scores for a specific week.")
    @app_commands.checks.has_role("Admin")
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
    @app_commands.command(name="late_reminder", description="Admin only: Remind all teams who haven’t submitted this week")
    @app_commands.describe(target="Use 'all' to ping all late teams.")
    @app_commands.checks.has_role("Admin")
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

    # 🧾 Archive scores to CSV
    @app_commands.command(name="archive_scores", description="Admin only: Export all scores to archive.csv")
    @app_commands.checks.has_role("Admin")
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
            await interaction.response.send_message("🧾 All scores exported to `archive.csv`!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to archive scores.\nError: `{str(e)}`", ephemeral=True)

    # 🛠️ Show admin help menu
    @app_commands.command(name="admin_help", description="Admin only: View a list of admin commands and what they do")
    @app_commands.checks.has_role("Admin")
    async def admin_help(self, interaction: discord.Interaction):
        msg = (
            "**🛠️ Admin Commands Overview**\n"
            "`/reset_week` — Delete all scores for a week\n"
            "`/lock_week` — Prevent score edits for a week\n"
            "`/unlock_week` — Allow score edits for a week\n"
            "`/late_reminder all` — DM all late teams\n"
            "`/archive_scores` — Export scores to CSV\n"
            "`/admin_help` — Show this menu"
        )
        await interaction.response.send_message(msg, ephemeral=True)

# 🔁 Cog loader
async def setup(bot):
    await bot.add_cog(AdminTools(bot))
