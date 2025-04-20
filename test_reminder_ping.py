import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from utils.week_tracker import get_current_week
from commands.weekly_reminder_tasks import WeeklyReminderTasks

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    cog = WeeklyReminderTasks(bot)
    await cog.send_reminders(hours_remaining=5)  # Simulates a Sunday-style reminder with hour warning
    await bot.close()

bot.run(TOKEN)
