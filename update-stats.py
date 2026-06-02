import os
import requests
from datetime import datetime, timezone

USERNAME = "Xyroine"
TOKEN = os.environ.get("GH_TOKEN", "")

headers = {
    "Authorization": f"bearer {TOKEN}",
    "Content-Type": "application/json"
}

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
created_at = data["createdAt"][:7]
created_label = datetime.strptime(created_at, "%Y-%m").strftime("%b %Y")

weeks = data["contributionsCollection"]["contributionCalendar"]["weeks"]
all_days = []
for week in weeks:
    for day in week["contributionDays"]:
        all_days.append(day)
all_days.sort(key=lambda d: d["date"])

today = datetime.now(timezone.utc).date()

# longest streak
longest_streak = 0
tmp = 0
longest_start = None
longest_end = None
cs = None
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

# current streak
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
        longest_date = f"{longest_start.strftime('%b %-d')} - {longest_end.strftime('%-d, %Y')}"
    else:
        longest_date = f"{longest_start.strftime('%b %-d')} - {longest_end.strftime('%b %-d, %Y')}"
else:
    longest_date = "-"

max_dash = 180
streak_dash = min(round((current_streak / 30) * max_dash), max_dash) if current_streak > 0 else 4
updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

print(f"Total: {total}, Streak: {current_streak}, Longest: {longest_streak}")
print(f"Streak date: {streak_date}, Longest date: {longest_date}")

# Tulis SVG langsung dari scratch (bukan replace template)
svg = f"""<svg width="100%" viewBox="0 0 680 180" role="img" xmlns="http://www.w3.org/2000/svg">
  <title>GitHub Stats — Xyroine</title>
  <defs>
    <style>
      .mono {{ font-family: 'Space Mono','Courier New',monospace; }}
      @keyframes appear {{ from{{opacity:0;transform:translateY(6px)}} to{{opacity:1;transform:translateY(0)}} }}
      @keyframes pulse {{ 0%,100%{{opacity:1}} 50%{{opacity:0.4}} }}
      .a1 {{ animation: appear .6s ease forwards .1s; opacity:0; }}
      .a2 {{ animation: appear .6s ease forwards .3s; opacity:0; }}
      .a3 {{ animation: appear .6s ease forwards .5s; opacity:0; }}
      .a4 {{ animation: appear .6s ease forwards .7s; opacity:0; }}
      .dot {{ animation: pulse 1.4s ease-in-out infinite; }}
    </style>
  </defs>
  <rect width="680" height="180" fill="#0d1117" rx="0"/>
  <rect width="680" height="2" fill="#00ff88" opacity="0.7" rx="1"/>
  <rect width="680" height="1.5" fill="#00ff88" opacity="0.04" rx="1">
    <animateTransform attributeName="transform" type="translate" values="0,0;0,180" dur="4s" repeatCount="indefinite"/>
  </rect>
  <text class="mono" x="28" y="26" fill="#484f58" font-size="9" letter-spacing="2">// GIT LOG --STATS XYROINE</text>
  <line x1="240" y1="40" x2="240" y2="148" stroke="#21262d" stroke-width="1"/>
  <line x1="440" y1="40" x2="440" y2="148" stroke="#21262d" stroke-width="1"/>
  <g class="a1">
    <text class="mono" x="120" y="62" text-anchor="middle" fill="#00ff8866" font-size="9" letter-spacing="2">CONTRIBUTIONS</text>
    <text class="mono" x="120" y="108" text-anchor="middle" fill="#00ff88" font-size="44" font-weight="700">{total}</text>
    <text class="mono" x="120" y="128" text-anchor="middle" fill="#484f58" font-size="9">{created_label} - Present</text>
  </g>
  <g class="a2">
    <circle cx="340" cy="96" r="34" fill="none" stroke="#21262d" stroke-width="3"/>
    <circle cx="340" cy="96" r="34" fill="none" stroke="#fbbf24" stroke-width="3"
      stroke-dasharray="{streak_dash} 214" stroke-linecap="round"
      transform="rotate(-90 340 96)"/>
    <text x="340" y="80" text-anchor="middle" font-size="13">&#x1F525;</text>
    <text class="mono" x="340" y="106" text-anchor="middle" fill="#fbbf24" font-size="28" font-weight="700">{current_streak}</text>
    <text class="mono" x="340" y="62" text-anchor="middle" fill="#fbbf2466" font-size="9" letter-spacing="2">CURRENT STREAK</text>
    <text class="mono" x="340" y="142" text-anchor="middle" fill="#484f58" font-size="9">{streak_date}</text>
  </g>
  <g class="a3">
    <text class="mono" x="560" y="62" text-anchor="middle" fill="#a78bfa66" font-size="9" letter-spacing="2">LONGEST STREAK</text>
    <text class="mono" x="560" y="108" text-anchor="middle" fill="#a78bfa" font-size="44" font-weight="700">{longest_streak}</text>
    <text class="mono" x="560" y="128" text-anchor="middle" fill="#484f58" font-size="9">{longest_date}</text>
  </g>
  <rect x="28" y="156" width="8" height="8" rx="4" fill="#00ff88" class="dot"/>
  <text class="mono a4" x="44" y="164" fill="#484f58" font-size="9" letter-spacing="1">STATUS: <tspan fill="#00ff88">ONLINE</tspan>  ·  LAST UPDATED: <tspan fill="#00ff88">{updated_at}</tspan></text>
  <rect y="178" width="680" height="2" fill="#00ff88" opacity="0.7" rx="1"/>
</svg>"""

with open("github-stats.svg", "w") as f:
    f.write(svg)

print("Done! SVG written.")
