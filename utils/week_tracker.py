# utils/week_tracker.py
from datetime import datetime, timezone, timedelta

SEASON_START = datetime(2025, 4, 14, 0, 0, tzinfo=timezone.utc)

def get_current_week():
    now = datetime.now(timezone.utc)
    days_since_start = (now - SEASON_START).days
    week = (days_since_start // 7) + 1
    return max(1, min(week, 10))  # Bound it between Week 1 and Week 10
