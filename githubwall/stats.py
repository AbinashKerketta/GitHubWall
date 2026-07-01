from datetime import datetime, timedelta
import time


def compute_streak(events):
    contribution_dates = set()
    for ev in events:
        created = ev.get("created_at", "")
        if created:
            try:
                dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                contribution_dates.add(dt.date())
            except (ValueError, AttributeError):
                pass

    if not contribution_dates:
        return {"longest_streak": 0, "current_streak": 0, "total_contributions": 0}

    today = datetime.now().astimezone().date()
    sorted_dates = sorted(contribution_dates)

    longest = 0
    current_run = 1
    for i in range(1, len(sorted_dates)):
        diff = (sorted_dates[i] - sorted_dates[i - 1]).days
        if diff == 1:
            current_run += 1
        elif diff > 1:
            longest = max(longest, current_run)
            current_run = 1
    longest = max(longest, current_run)

    current_streak = 0
    check = today
    while check in contribution_dates:
        current_streak += 1
        check -= timedelta(days=1)

    return {
        "longest_streak": longest,
        "current_streak": current_streak,
        "total_contributions": len(contribution_dates),
    }
