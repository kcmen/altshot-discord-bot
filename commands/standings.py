import sqlite3
import discord
from discord import app_commands, Interaction
from discord.ext import commands

class Standings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="standings", description="Show current team rankings")
    async def standings(self, interaction: Interaction):
        try:
            conn = sqlite3.connect("scores.db")
            cursor = conn.cursor()
            cursor.execute("SELECT team, result FROM scores")
            rows = cursor.fetchall()
            conn.close()

            points = {}
            for team, result in rows:
                if team not in points:
                    points[team] = {"W": 0, "T": 0, "L": 0, "P": 0}
                if result.upper() == "AS":
                    points[team]["T"] += 1
                    points[team]["P"] += 1
                elif "&" in result:
                    points[team]["W"] += 1
                    points[team]["P"] += 2
                elif result.upper() == "FORFEIT":
                    points[team]["L"] += 1
                else:
                    points[team]["L"] += 1

            leaderboard = sorted(points.items(), key=lambda x: x[1]["P"], reverse=True)
            msg = "\U0001F3C6 **Alt Shot Circuit Standings**\n"
            for team, data in leaderboard:
                msg += f"{team}: {data['P']} pts (W:{data['W']} T:{data['T']} L:{data['L']})\n"
            await interaction.response.send_message(msg)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error fetching standings: {e}")

async def setup(bot):
    await bot.add_cog(Standings(bot))
