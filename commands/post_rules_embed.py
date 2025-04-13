import discord
from discord.ext import commands
from discord import app_commands

RULES_CHANNEL_ID = 1359988590536429861  # Update if needed

class PostRulesEmbed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="post_rules", description="Post the official Alt Shot Circuit rules as an embed")
    async def post_rules(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📜 ALT SHOT CIRCUIT – OFFICIAL RULES",
            description=(
                "**⛳ MATCH FORMAT**\n"
                "- Alternate Shot (2v2)\n"
                "- 18 holes per match\n"
                "- Fixed teammates for the full season\n\n"
                "**🗓️ WEEKLY DEADLINE**\n"
                "- Week opens: Sunday @ 8:00 PM EST\n"
                "- Week ends: Sunday @ 6:59 PM EST (following week)\n"
                "- No extensions unless approved by an admin\n\n"
                "**📸 SCORE SUBMISSION**\n"
                "- Screenshot required in #score-submission\n"
                "- Must show both team names and final result (e.g. 3&2, AS, 1UP)\n\n"
                "**🔒 WEEKLY LOCK RULE**\n"
                "- Scores and edits must be submitted before the deadline\n"
                "- Locked weeks cannot be changed unless cleared by an admin\n\n"
                "**🎯 SCORING SYSTEM**\n"
                "- Win = 1 Point\n"
                "- Tie = 0.5 Points\n"
                "- Loss = 0 Points\n"
                "- Hole Differential used as tiebreaker\n\n"
                "**🏆 PLAYOFF FORMAT**\n"
                "- Top 8 teams advance after Week 8\n"
                "- Bracket: Quarterfinals → Semifinals → Finals\n"
                "- Tied playoff matches go to sudden death\n\n"
                "**🚨 CONDUCT & SPORTSMANSHIP**\n"
                "- Be respectful to teammates and opponents\n"
                "- No quitting early — all matches must be completed\n"
                "- Trash talk is allowed, disrespect is not\n\n"
                "**🔐 ADMIN TOOLS**\n"
                "Admin-only commands manage schedules, scores, and locks.\n"
                "Staff tools are pinned privately in #lcs-season-guide."
            ),
            color=discord.Color.dark_gold()
        )

        channel = self.bot.get_channel(RULES_CHANNEL_ID)
        if channel:
            await channel.send(embed=embed)
            await interaction.response.send_message("✅ Rules embed posted to #rules.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Could not find the rules channel.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(PostRulesEmbed(bot))
