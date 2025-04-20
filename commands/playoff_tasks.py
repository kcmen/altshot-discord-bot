import discord
from discord.ext import commands, tasks
from datetime import datetime
from utils.team_name_loader import get_team_name
from generate_playoff_bracket import generate_quarterfinals
from advance_playoff_logic import generate_semifinals_from_scores, generate_finals_from_scores

PLAYOFF_CHANNEL_ID = 1359236509131079933

class PlayoffTasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_playoff_rounds.start()

    def cog_unload(self):
        self.check_playoff_rounds.cancel()

    @tasks.loop(minutes=5)
    async def check_playoff_rounds(self):
        now = datetime.utcnow()
        week_9_time = datetime(2025, 6, 9, 0, 0, 0)
        week_10_time = datetime(2025, 6, 16, 0, 0, 0)

        if week_9_time <= now < week_10_time:
            await self.post_quarters_and_semis()
            self.check_playoff_rounds.cancel()
        elif now >= week_10_time:
            await self.post_finals_auto()
            self.check_playoff_rounds.cancel()

    async def post_quarters_and_semis(self):
        qfs = generate_quarterfinals()
        if not qfs:
            return

        qf_lines = []
        for i, (t1, t2) in enumerate(qfs, 1):
            qf_lines.append(f"**QF{i}:** {get_team_name(t1)} ({t1}) 🆚 {get_team_name(t2)} ({t2})")

        sf = generate_semifinals_from_scores()
        if sf:
            sf_lines = []
            for i, (w1, w2) in enumerate(sf, 1):
                sf_lines.append(f"**SF{i}:** {get_team_name(w1)} ({w1}) 🆚 {get_team_name(w2)} ({w2})")
        else:
            sf_lines = [
                "**SF1:** Winner QF1 🆚 Winner QF2",
                "**SF2:** Winner QF3 🆚 Winner QF4"
            ]

        message = "🏆 **Alt Shot Circuit Playoffs – Quarterfinals & Semifinals**\n\n"
        message += "\n".join(qf_lines) + "\n\n" + "\n".join(sf_lines)

        channel = self.bot.get_channel(PLAYOFF_CHANNEL_ID)
        if channel:
            await channel.send(message)

    async def post_finals_auto(self):
        finals = generate_finals_from_scores()
        if not finals:
            return

        champ = finals["Championship"]
        third = finals["Third Place"]

        message = (
            "🏆 **Alt Shot Circuit Playoffs – Finals & 3rd Place Match**\n\n"
            f"🥇 **Championship Match:** {get_team_name(champ[0])} ({champ[0]}) 🆚 {get_team_name(champ[1])} ({champ[1]})\n"
            f"🥉 **3rd Place Match:** {get_team_name(third[0])} ({third[0]}) 🆚 {get_team_name(third[1])} ({third[1]})"
        )

        channel = self.bot.get_channel(PLAYOFF_CHANNEL_ID)
        if channel:
            await channel.send(message)

    @check_playoff_rounds.before_loop
    async def before_posting(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(PlayoffTasks(bot))
