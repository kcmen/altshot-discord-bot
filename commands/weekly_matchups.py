import discord
from discord.ext import tasks, commands
from datetime import datetime
from utils.week_tracker import get_current_week
from utils.team_name_loader import get_team_name

# Channel to post matchups
MATCHUP_CHANNEL_ID = 1356480122026328064  # replace with your actual channel ID

# Matchups for each week
MATCHUPS_BY_WEEK = {
    1: [("T1", "T2"), ("T3", "T4"), ("T5", "T6"), ("T7", "T8"), ("T9", "T10"),
        ("T11", "T12"), ("T13", "T14"), ("T15", "T16"), ("T17", "T18"), ("T19", "T20")],
    2: [("T1", "T3"), ("T2", "T4"), ("T5", "T7"), ("T6", "T8"), ("T9", "T11"),
        ("T10", "T12"), ("T13", "T15"), ("T14", "T16"), ("T17", "T19"), ("T18", "T20")],
    3: [("T1", "T4"), ("T2", "T5"), ("T3", "T6"), ("T7", "T9"), ("T8", "T10"),
        ("T11", "T13"), ("T12", "T14"), ("T15", "T17"), ("T16", "T18"), ("T19", "T20")],
    4: [("T1", "T5"), ("T2", "T6"), ("T3", "T7"), ("T4", "T8"), ("T9", "T13"),
        ("T10", "T14"), ("T11", "T15"), ("T12", "T16"), ("T17", "T20"), ("T18", "T19")],
    5: [("T1", "T6"), ("T2", "T7"), ("T3", "T8"), ("T4", "T9"), ("T5", "T10"),
        ("T11", "T16"), ("T12", "T15"), ("T13", "T18"), ("T14", "T17"), ("T19", "T20")],
    6: [("T1", "T7"), ("T2", "T8"), ("T3", "T9"), ("T4", "T10"), ("T5", "T11"),
        ("T6", "T12"), ("T13", "T19"), ("T14", "T20"), ("T15", "T17"), ("T16", "T18")],
    7: [("T1", "T8"), ("T2", "T9"), ("T3", "T10"), ("T4", "T11"), ("T5", "T12"),
        ("T6", "T13"), ("T7", "T14"), ("T15", "T20"), ("T16", "T19"), ("T17", "T18")],
    8: [("T1", "T9"), ("T2", "T10"), ("T3", "T11"), ("T4", "T12"), ("T5", "T13"),
        ("T6", "T14"), ("T7", "T15"), ("T8", "T16"), ("T17", "T20"), ("T18", "T19")],
}

class MatchupPoster(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.post_matchups.start()

    def cog_unload(self):
        self.post_matchups.cancel()

    @tasks.loop(minutes=5)
    async def post_matchups(self):
        now = datetime.utcnow()
        # Sunday 8 PM EST = Monday 12 AM GMT
        if now.weekday() == 6 and now.hour == 0 and now.minute < 5:
            week = get_current_week()
            matchups = MATCHUPS_BY_WEEK.get(week, [])

            if not matchups:
                return

            lines = []
            for t1, t2 in matchups:
                name1 = get_team_name(t1)
                name2 = get_team_name(t2)
                lines.append(f"📌 **{name1} ({t1})** vs **{name2} ({t2})**")

            message = f"## 📅 **Week {week} Matchups**\n" + "\n".join(lines)

            channel = self.bot.get_channel(MATCHUP_CHANNEL_ID)
            if channel:
                await channel.send(message)

    @post_matchups.before_loop
    async def before_posting(self):
        await self.bot.wait_until_ready()

# Register cog
async def setup(bot):
    await bot.add_cog(MatchupPoster(bot))
