import os
import re
import urllib.request
import json

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

SHORT_DESCS = {
    "VaultCore": "Ledger wallet service (Java 21, Spring Boot, PostgreSQL, Docker)",
    "CodeTogether": "Real-time collaborative code editor (Monaco, Yjs/CRDT)",
    "CardioLens": "Cardiovascular risk assessment system (Python)",
    "Nilami": "Real-time auction & bidding platform (TypeScript)",
    "Rozgaar": "Community job portal for local opportunities (JavaScript)",
    "ProctorDesign": "Online exam platform with AI proctoring (Django REST, React)",
    "promptFlow-AI": "Academic publication tracking platform (FastAPI, React)",
    "MeetScribe": "AI meeting notes and action items (FastAPI, React)",
    "BharatBazzar": "Full-stack e-commerce solution (React, Node.js)",
    "Developer-Learning-Tracker": "DSA progress and stats tracking app (MERN)",
    "Emulator_8086": "Intel 8086 microprocessor simulator (Tauri)",
    "CozyStays-HotelRoomBookingSystem": "Hotel booking management platform (MERN)",
    "speak-Ease-Duolingo-Clone": "Language learning app with gamified lessons (MERN)",
}

DEFAULT_EMOJI = "📦"

filtered_repos = []
for r in repos:
    if r.get("name") == USERNAME or r.get("fork"):
        continue
    filtered_repos.append(r)
    if len(filtered_repos) >= 5:
        break

lines = []
for r in filtered_repos:
    name = r.get("name", "")
    html_url = r.get("html_url", f"https://github.com/{USERNAME}/{name}")
    raw_desc = r.get("description") or "Repository"
    lang = r.get("language") or "Code"
    if name in SHORT_DESCS:
        desc = SHORT_DESCS[name]
    else:
        words = raw_desc.split()
        desc = " ".join(words[:7]) + (f" ({lang})" if lang else "")
    emoji = EMOJIS.get(name, DEFAULT_EMOJI)
    lines.append(f"- {emoji} **[{name}]({html_url})** — {desc}")

new_content = "\n".join(lines)

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

pattern = r"(<!-- RECENT_REPOS:START -->\n)(?:[\s\S]*?)(\n<!-- RECENT_REPOS:END -->)"
if re.search(pattern, readme):
    replacement = r"\g<1>" + new_content + r"\g<2>"
    updated_readme = re.sub(pattern, replacement, readme)
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated_readme)
    print("Successfully updated README.md with recent repositories.")
else:
    print("RECENT_REPOS markers not found in README.md.")
