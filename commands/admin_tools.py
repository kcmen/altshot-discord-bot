import sqlite3
import discord
from discord import app_commands

# 🔒 Lock a week (Admin only)
@app_commands.command(name="lock_week", description="Lock a specific week to prevent editing")
@app_commands.describe(week="Week number to lock")
async def lock_week(interaction: discord.Interaction, week: int):
    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO locks (week, locked)
        VALUES (?, 1)
        ON CONFLICT(week) DO UPDATE SET locked = 1
    """, (week,))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"🔒 Week {week} is now locked.")

# 🔓 Unlock a week (Admin only)
@app_commands.command(name="unlock_week", description="Unlock a specific week to allow score updates")
@app_commands.describe(week="Week number to unlock")
async def unlock_week(interaction: discord.Interaction, week: int):
    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE locks SET locked = 0 WHERE week = ?
    """, (week,))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"🔓 Week {week} is now unlocked.")

# Register the commands
async def setup(bot):
    bot.tree.add_command(lock_week)
    bot.tree.add_command(unlock_week)
