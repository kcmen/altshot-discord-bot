import sqlite3
import discord
from discord import app_commands
from utils.format_leaderboard import format_leaderboard

LEADERBOARD_CHANNEL_ID = 1356480492396089394  # 👈 Replace with your real channel ID
current_week = 1

# Internal function to post leaderboard to the designated channel
async def post_leaderboard(client: discord.Client):
    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()
    cursor.execute("SELECT team, result FROM scores")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return

    leaderboard_text = format_leaderboard(rows)
    leaderboard_text = f"📆 **Leaderboard after Week {current_week}**\n\n" + leaderboard_text

    guild = client.get_guild(1356460160239010026)  # Replace with your real guild ID
    leaderboard_channel = guild.get_channel(LEADERBOARD_CHANNEL_ID)

    if leaderboard_channel:
        await leaderboard_channel.send(f"🏆 **Alt Shot Leaderboard Update**\n{leaderboard_text}")

# /leaderboard — posts leaderboard manually (admin only)
@app_commands.command(name="update_leaderboard", description="Force post the leaderboard (Admin only)")
@app_commands.checks.has_permissions(administrator=True)
async def update_leaderboard(interaction: discord.Interaction):
    await post_leaderboard(interaction.client)
    await interaction.response.send_message("📬 Leaderboard manually posted.", ephemeral=True)

# Register commands
async def setup(bot):
    bot.tree.add_command(update_leaderboard)

    # Also expose post_leaderboard for other modules to call
    import sys
    sys.modules[__name__].post_leaderboard = post_leaderboard
