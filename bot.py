print("\U0001F680 bot.py starting up...")

import os
import sqlite3
from dotenv import load_dotenv
import discord
from discord.ext import commands

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = discord.Object(id=1356460160239010026)  # AHGA Test Server

# Setup intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Ensure locks table exists
def ensure_locks_table():
    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS locks (
            week INTEGER PRIMARY KEY,
            locked INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def is_week_locked(week):
    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()
    cursor.execute("SELECT locked FROM locks WHERE week = ?", (week,))
    row = cursor.fetchone()
    conn.close()
    return row is not None and row[0] == 1

def lock_week(week):
    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO locks (week, locked) VALUES (?, 1) "
        "ON CONFLICT(week) DO UPDATE SET locked = 1",
        (week,)
    )
    conn.commit()
    conn.close()

def unlock_week(week):
    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE locks SET locked = 0 WHERE week = ?", (week,))
    conn.commit()
    conn.close()

# Make lock helpers globally available
bot.is_week_locked = is_week_locked
bot.lock_week = lock_week
bot.unlock_week = unlock_week

@bot.event
async def on_ready():
    ensure_locks_table()
    print(f"✅ Bot is now online as {bot.user}")
    try:
        await bot.tree.clear_commands(guild=GUILD_ID)
        # Temporarily sync as GLOBAL instead of to the guild
        synced = await bot.tree.sync()
        print(f"🌐 Synced {len(synced)} global command(s)")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

# Load all command modules
initial_extensions = [
    "commands.matchup",
    "commands.scores",
    "commands.standings",
    "commands.results_week",
    "commands.hole_diff",
    "commands.admin_tools",
    "commands.reminders",
    "commands.schedule",
    "commands.leaderboard",
    "commands.weekly_matchups",
    "commands.team_codes",
    "commands.weekly_reminder_tasks",
    "commands.post_playoff_bracket",
    "commands.report_playoff_score",
    "commands.view_playoff_score",
    "commands.delete_playoff_score",
    "commands.reset_playoffs",
    "commands.advance_manually"
]

async def load_extensions():
    for ext in initial_extensions:
        try:
            await bot.load_extension(ext)
            print(f"✅ Loaded extension: {ext}")
        except Exception as e:
            print(f"❌ Failed to load extension {ext}: {e}")

@bot.event
async def setup_hook():
    await load_extensions()

# Run the bot
if __name__ == "__main__":
    bot.run(TOKEN)
