import os
import re
import urllib.request
import json
from datetime import datetime

USERNAME = "AP24110011314"
URL = f"https://api.github.com/users/{USERNAME}/repos?sort=pushed&per_page=15"

headers = {
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": f"{USERNAME}-profile-updater",
}
token = os.environ.get("GITHUB_TOKEN")
if token:
    headers["Authorization"] = f"Bearer {token}"

req = urllib.request.Request(URL, headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        repos = json.loads(response.read().decode())
except Exception as e:
    print(f"Error fetching repos: {e}")
    exit(0)

EMOJIS = {
    "VaultCore": "🪙",
    "CardioLens": "🫀",
    "Nilami": "🔨",
    "Rozgaar": "💼",
    "CodeTogether": "👥",
    "ProctorDesign": "🛡️",
    "promptFlow-AI": "🔬",
    "MeetScribe": "🎙️",
    "BharatBazzar": "🛒",
    "Developer-Learning-Tracker": "📊",
    "Emulator_8086": "🖥️",
    "CozyStays-HotelRoomBookingSystem": "🏨",
    "speak-Ease-Duolingo-Clone": "🗣️",
}

DEFAULT_EMOJI = "📦"

filtered_repos = []
for r in repos:
    # Exclude profile repository itself and forks
    if r.get("name") == USERNAME or r.get("fork"):
        continue
    filtered_repos.append(r)
    if len(filtered_repos) >= 5:
        break

lines = []
for r in filtered_repos:
    name = r.get("name", "")
    html_url = r.get("html_url", f"https://github.com/{USERNAME}/{name}")
    desc = r.get("description") or "Repository"
    lang = r.get("language") or "Code"
    pushed_at = r.get("pushed_at", "")
    date_str = ""
    if pushed_at:
        try:
            dt = datetime.strptime(pushed_at, "%Y-%m-%dT%H:%M:%SZ")
            date_str = dt.strftime("%b %d, %Y")
        except Exception:
            date_str = pushed_at[:10]
    emoji = EMOJIS.get(name, DEFAULT_EMOJI)
    suffix = f" · *Updated {date_str}*" if date_str else ""
    lines.append(f"- {emoji} **[{name}]({html_url})** — {desc} ({lang}){suffix}")

new_content = "\n".join(lines)

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

pattern = r"(<!-- RECENT_REPOS:START -->\n)(?:[\s\S]*?)(\n<!-- RECENT_REPOS:END -->)"
replacement = r"\g<1>" + new_content + r"\g<2>"
updated_readme = re.sub(pattern, replacement, readme)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(updated_readme)

print("Successfully updated README.md with recent repositories.")
