import os
import sqlite3
import json
import random
from itertools import combinations
from dotenv import load_dotenv
import discord
from discord.ext import commands

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Setup intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Ensure scores table exists
def ensure_scores_table():
    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team TEXT,
            opponent TEXT,
            week INTEGER,
            result TEXT,
            holes_won INTEGER,
            submitted_by TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

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
        "ON CONFLICT(week) DO UPDATE SET locked = 1", (week,)
    )
    conn.commit()
    conn.close()

def unlock_week(week):
    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE locks SET locked = 0 WHERE week = ?", (week,))
    conn.commit()
    conn.close()

# Auto-generate schedule.json if missing
def auto_generate_schedule():
    if not os.path.exists("teams.json"):
        print("⚠️ teams.json not found. Skipping schedule generation.")
        return
    if os.path.exists("schedule.json"):
        print("✅ schedule.json already exists. Skipping generation.")
        return

    with open("teams.json", "r") as f:
        data = json.load(f)
    teams = list(data.keys())
    print(f"📋 Generating schedule for {len(teams)} teams: {teams}")

    total_matchups = list(combinations(teams, 2))
    random.shuffle(total_matchups)

    schedule = [[] for _ in range(8)]
    team_usage = {team: 0 for team in teams}

    for team1, team2 in total_matchups:
        for week in schedule:
            scheduled_teams = [t for match in week for t in match]
            if team1 not in scheduled_teams and team2 not in scheduled_teams:
                week.append((team1, team2))
                team_usage[team1] += 1
                team_usage[team2] += 1
                break
        if all(count >= 8 for count in team_usage.values()):
            break

    full_schedule = {}
    for i, week in enumerate(schedule):
        full_schedule[f"Week {i+1}"] = [[t1, t2] for t1, t2 in week]

    with open("schedule.json", "w") as f:
        json.dump(full_schedule, f, indent=4)

    print("✅ schedule.json generated successfully.")

# Make lock helpers globally available
bot.is_week_locked = is_week_locked
bot.lock_week = lock_week
bot.unlock_week = unlock_week

# Load all command modules
initial_extensions = [
    "commands.matchup",
    "commands.scores",
    "commands.standings",
    "commands.hole_diff",
    "commands.schedule",
    "commands.leaderboard",
    "commands.post_playoff_bracket",
    "commands.report_playoff_score",
    "commands.view_playoff_score",
    "commands.delete_playoff_score",
    "commands.reset_playoffs",
    "commands.advance_manually",
    "commands.reset_season",
    "commands.weekly_lock_task",
    "commands.weekly_post_matchups",
    "commands.weekly_results_task",
    "commands.post_team_pairings",
    "commands.unlock_week",
    "commands.view_tracker" # ✅ Added this line
]


async def load_extensions():
    for ext in initial_extensions:
        try:
            await bot.load_extension(ext)
            print(f"✅ Loaded extension: {ext}")
        except Exception as e:
            print(f"❌ Failed to load extension {ext}: {e}")

@bot.event
async def on_ready():
    print(f"🚀 {bot.user} is now online and ready!")

@bot.event
async def on_command_error(ctx, error):
    print(f"❌ An error occurred: {error}")

@bot.event
async def setup_hook():
    await bot.load_extension("commands.admin_tools")
    await load_extensions()

    try:
        synced = await bot.tree.sync()
        print(f"🌐 Synced {len(synced)} global command(s)")

        TEST_GUILD_ID = 1256795396353560697
        guild = discord.Object(id=TEST_GUILD_ID)
        guild_synced = await bot.tree.sync(guild=guild)
        print(f"🏠 Synced {len(guild_synced)} commands to test guild {TEST_GUILD_ID}")

    except Exception as e:
        print(f"❌ Failed to sync slash commands: {e}")

    auto_generate_schedule()
    ensure_scores_table()
    ensure_locks_table()

# ✅ RUN ONLY IF MAIN SCRIPT
if __name__ == "__main__":
    bot.run(TOKEN)
