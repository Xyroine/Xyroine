import os
import re
import math
import requests
from datetime import datetime, timezone, timedelta

USERNAME = "Xyroine"
TOKEN = os.environ.get("GH_TOKEN", "")

headers = {
    "Authorization": f"bearer {TOKEN}",
    "Content-Type": "application/json"
}

# GraphQL query — contributions + streak data
query = """
query($login: String!) {
  user(login: $login) {
    createdAt
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""

resp = requests.post(
    "https://api.github.com/graphql",
    json={"query": query, "variables": {"login": USERNAME}},
    headers=headers
)
data = resp.json()["data"]["user"]

total = data["contributionsCollection"]["contributionCalendar"]["totalContributions"]
created_at = data["createdAt"][:7]  # e.g. "2023-05"
created_label = datetime.strptime(created_at, "%Y-%m").strftime("%b %Y")

# flatten all days sorted
weeks = data["contributionsCollection"]["contributionCalendar"]["weeks"]
all_days = []
for week in weeks:
    for day in week["contributionDays"]:
        all_days.append(day)
all_days.sort(key=lambda d: d["date"])

# compute current streak & longest streak
today = datetime.now(timezone.utc).date()
current_streak = 0
longest_streak = 0
tmp = 0
longest_start = None
longest_end = None
cur_start = None

for day in all_days:
    d = datetime.strptime(day["date"], "%Y-%m-%d").date()
    if d > today:
        break
    if day["contributionCount"] > 0:
        tmp += 1
        if tmp == 1:
            cs = d
        if tmp > longest_streak:
            longest_streak = tmp
            longest_start = cs
            longest_end = d
    else:
        tmp = 0

# recalc current streak from today backwards
current_streak = 0
for day in reversed(all_days):
    d = datetime.strptime(day["date"], "%Y-%m-%d").date()
    if d > today:
        continue
    if day["contributionCount"] > 0:
        current_streak += 1
    else:
        break

streak_date = today.strftime("%b %-d, %Y") if current_streak > 0 else "No active streak"

if longest_start and longest_end:
    if longest_start.month == longest_end.month:
        longest_date = f"{longest_start.strftime('%b %-d')} – {longest_end.strftime('%-d, %Y')}"
    else:
        longest_date = f"{longest_start.strftime('%b %-d')} – {longest_end.strftime('%b %-d, %Y')}"
else:
    longest_date = "—"

# ring dash: circumference = 2*pi*34 ≈ 213.6, max at 30 days
max_dash = 180
streak_dash = min(round((current_streak / 30) * max_dash), max_dash) if current_streak > 0 else 4

updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

# read template and fill
with open("github-stats.svg", "r") as f:
    svg = f.read()

svg = svg.replace("{{CONTRIBUTIONS}}", str(total))
svg = svg.replace("{{CONTRIB_SINCE}}", created_label)
svg = svg.replace("{{CURRENT_STREAK}}", str(current_streak))
svg = svg.replace("{{STREAK_DATE}}", streak_date)
svg = svg.replace("{{LONGEST_STREAK}}", str(longest_streak))
svg = svg.replace("{{LONGEST_DATE}}", longest_date)
svg = svg.replace("{{STREAK_DASH}}", str(streak_dash))
svg = svg.replace("{{UPDATED_AT}}", updated_at)

with open("github-stats.svg", "w") as f:
    f.write(svg)

print(f"✅ Stats updated: {total} contributions, streak {current_streak}, longest {longest_streak}")
