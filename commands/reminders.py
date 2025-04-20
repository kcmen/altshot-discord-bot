import discord
from discord import app_commands

# /reminder command
@app_commands.command(name="reminder", description="Send a DM to a user reminding them to report their score")
@app_commands.describe(user="The user you want to remind")
async def reminder(interaction: discord.Interaction, user: discord.User):
    try:
        dm_channel = await user.create_dm()
        await dm_channel.send("⏰ Friendly reminder to report your Alt Shot Circuit score!")
        await interaction.response.send_message(f"✅ Reminder sent to {user.display_name} via DM.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to send reminder: {e}", ephemeral=True)

# Register the command
async def setup(bot):
    bot.tree.add_command(reminder)
