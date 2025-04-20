import asyncio
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from commands.weekly_matchups import MATCHUPS_BY_WEEK
from utils.week_tracker import get_current_week
from utils.team_name_loader import get_team_name

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
MATCHUP_CHANNEL_ID = 1356480122026328064

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

    week = get_current_week()
    matchups = MATCHUPS_BY_WEEK.get(week, [])

    if not matchups:
        print("❌ No matchups for the current week.")
        await bot.close()
        return

    lines = []
    for t1, t2 in matchups:
        name1 = get_team_name(t1)
        name2 = get_team_name(t2)
        lines.append(f"📌 **{name1} ({t1})** vs **{name2} ({t2})**")

    message = f"## 📅 **Week {week} Matchups**\n" + "\n".join(lines)

    channel = bot.get_channel(MATCHUP_CHANNEL_ID)
    if channel:
        await channel.send(message)
        print("✅ Matchups posted!")
    else:
        print("❌ Could not find the channel.")

    await bot.close()

bot.run(TOKEN)
