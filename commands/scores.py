import sqlite3
from datetime import datetime
import discord
from discord import app_commands
from utils.week_tracker import get_current_week
from utils.team_name_loader import get_team_name

# Non-async helper to check if a week is locked
def is_week_locked(week):
    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()
    cursor.execute("SELECT locked FROM locks WHERE week = ?", (week,))
    row = cursor.fetchone()
    conn.close()
    return row is not None and row[0] == 1

# /score command
@app_commands.command(name="score", description="Report your Alt Shot match result")
@app_commands.describe(team="Your team (e.g. T3 or just 3)", result="Match result (e.g. 3&2, 1UP, or AS)")
async def report_score(interaction: discord.Interaction, team: str, result: str):
    week = get_current_week()
    if is_week_locked(week):
        await interaction.response.send_message(f"🔒 Week {week} is locked. You cannot submit a score.", ephemeral=True)
        return
    team = team.strip().upper()
    if not team.startswith("T"):
        team = f"T{team}"
    result = result.strip().upper().replace(" ", "")
    if result == "1UP":
        result = "1&0"
    valid_results = ["AS", "FORFEIT"] + [f"{i}&{j}" for i in range(1, 10) for j in range(0, 5)]
    if result not in valid_results:
        await interaction.response.send_message(f"❌ Invalid result format. Use `3&2`, `AS`, `1UP`, or `FORFEIT`.", ephemeral=True)
        return
    submitted_by = interaction.user.display_name
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO scores (team, result, week, submitted_by, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (team, result, week, submitted_by, timestamp))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"📝 Score reported for **{team}**: `{result}` by {submitted_by}")

    from commands.leaderboard import post_leaderboard
    await post_leaderboard(interaction.client)

# /view_score command (UPDATED)
@app_commands.command(name="view_score", description="View the score submitted for a specific team or week")
@app_commands.describe(team="Optional: Team to look up (e.g. T4 or just 4)", week="Optional: Week number to filter")
async def view_score(interaction: discord.Interaction, team: str = None, week: int = None):
    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()

    if team:
        team = team.strip().upper()
        if not team.startswith("T"):
            team = f"T{team}"
        if week:
            cursor.execute("""
                SELECT result, submitted_by, timestamp FROM scores 
                WHERE team = ? AND week = ? ORDER BY id DESC LIMIT 1
            """, (team, week))
        else:
            cursor.execute("""
                SELECT result, week, submitted_by, timestamp FROM scores 
                WHERE team = ? ORDER BY id DESC LIMIT 1
            """, (team,))
        row = cursor.fetchone()
        conn.close()
        if row:
            if week:
                result, submitted_by, timestamp = row
                await interaction.response.send_message(
                    f"🔍 **{team}** submitted `{result}` (Week {week}) by **{submitted_by}** on `{timestamp}`"
                )
            else:
                result, result_week, submitted_by, timestamp = row
                await interaction.response.send_message(
                    f"🔍 **{team}** submitted `{result}` (Week {result_week}) by **{submitted_by}** on `{timestamp}`"
                )
        else:
            await interaction.response.send_message(f"❌ No score found for **{team}**.", ephemeral=True)
    else:
        # No team specified — show all scores for the given or current week
        target_week = week if week else get_current_week()
        cursor.execute("""
            SELECT team, result, submitted_by, timestamp FROM scores
            WHERE week = ? ORDER BY team ASC
        """, (target_week,))
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            await interaction.response.send_message(f"❌ No scores found for Week {target_week}.", ephemeral=True)
            return
        msg = f"📋 **Scores for Week {target_week}:**\n"
        for team, result, submitted_by, timestamp in rows:
            msg += f"• **{team}** — `{result}` by {submitted_by} at {timestamp}\n"
        await interaction.response.send_message(msg)

# /edit_score command
@app_commands.command(name="edit_score", description="Edit the most recent score for a team")
@app_commands.describe(team="Team whose score needs to be corrected", new_result="New correct result (e.g. 3&2, AS)")
async def edit_score(interaction: discord.Interaction, team: str, new_result: str):
    week = get_current_week()
    if is_week_locked(week):
        await interaction.response.send_message(f"🔒 Week {week} is locked. You cannot edit scores.", ephemeral=True)
        return
    team = team.strip().upper()
    if not team.startswith("T"):
        team = f"T{team}"
    new_result = new_result.strip().upper().replace(" ", "")
    if new_result == "1UP":
        new_result = "1&0"
    valid_results = ["AS", "FORFEIT"] + [f"{i}&{j}" for i in range(1, 10) for j in range(0, 5)]
    if new_result not in valid_results:
        await interaction.response.send_message(f"❌ Invalid format. Use `3&2`, `AS`, or `1UP`.", ephemeral=True)
        return
    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM scores WHERE team = ? ORDER BY id DESC LIMIT 1", (team,))
    row = cursor.fetchone()
    if row:
        score_id = row[0]
        cursor.execute("UPDATE scores SET result = ?, timestamp = ? WHERE id = ?", (
            new_result,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            score_id
        ))
        conn.commit()
        conn.close()
        await interaction.response.send_message(f"✅ Updated score for **{team}** to `{new_result}`")

        from commands.leaderboard import post_leaderboard
        await post_leaderboard(interaction.client)
    else:
        conn.close()
        await interaction.response.send_message(f"❌ No score found for **{team}** to edit.", ephemeral=True)

# /delete_score command
@app_commands.command(name="delete_score", description="Delete the most recent score submitted for a team")
@app_commands.describe(team="Team whose score should be deleted")
async def delete_score(interaction: discord.Interaction, team: str):
    week = get_current_week()
    if is_week_locked(week):
        await interaction.response.send_message(f"🔒 Week {week} is locked. You cannot delete scores.", ephemeral=True)
        return
    team = team.strip().upper()
    if not team.startswith("T"):
        team = f"T{team}"
    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM scores WHERE team = ? ORDER BY id DESC LIMIT 1", (team,))
    row = cursor.fetchone()
    if row:
        score_id = row[0]
        cursor.execute("DELETE FROM scores WHERE id = ?", (score_id,))
        conn.commit()
        conn.close()
        await interaction.response.send_message(f"🗑️ Deleted latest score for **{team}**")

        from commands.leaderboard import post_leaderboard
        await post_leaderboard(interaction.client)
    else:
        conn.close()
        await interaction.response.send_message(f"❌ No score found for **{team}** to delete.", ephemeral=True)

# /submit_forfeit command
@app_commands.command(name="submit_forfeit", description="Mark your team as forfeiting the match")
@app_commands.describe(team="Your team forfeiting the match")
async def submit_forfeit(interaction: discord.Interaction, team: str):
    week = get_current_week()
    if is_week_locked(week):
        await interaction.response.send_message(f"🔒 Week {week} is locked. You cannot submit forfeits.", ephemeral=True)
        return
    team = team.strip().upper()
    if not team.startswith("T"):
        team = f"T{team}"
    submitted_by = interaction.user.display_name
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = "FORFEIT"
    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO scores (team, result, week, submitted_by, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (team, result, week, submitted_by, timestamp))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"🚫 **{team}** marked as a FORFEIT by {submitted_by}")

    from commands.leaderboard import post_leaderboard
    await post_leaderboard(interaction.client)

# /late_scores command
@app_commands.command(name="late_scores", description="Show teams that haven't reported this week")
async def late_scores(interaction: discord.Interaction):
    week = get_current_week()
    expected_teams = [f"T{i}" for i in range(1, 21)]
    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT team FROM scores WHERE week = ?", (week,))
    reported_teams = [row[0] for row in cursor.fetchall()]
    conn.close()
    missing_teams = [team for team in expected_teams if team not in reported_teams]
    if missing_teams:
        lines = "\n".join([f"❌ {team}" for team in missing_teams])
        await interaction.response.send_message(f"⏰ **Teams that haven't reported for Week {week}:**\n{lines}")
    else:
        await interaction.response.send_message("✅ All teams have submitted for this week!")

# Register all commands
async def setup(bot):
    bot.tree.add_command(report_score)
    bot.tree.add_command(view_score)
    bot.tree.add_command(edit_score)
    bot.tree.add_command(delete_score)
    bot.tree.add_command(submit_forfeit)
    bot.tree.add_command(late_scores)
