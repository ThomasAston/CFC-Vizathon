import requests
import json
from datetime import datetime
from dateutil.parser import isoparse

API_KEY = "1f640d32af86dbe571abc0cc153a9e0b"  # Replace with your actual API key
TEAM_ID = 49  # Chelsea FC

# Determine correct football season year
now = datetime.now()
SEASON = now.year - 1 if now.month < 7 else now.year
LIMIT = 3

headers = {
    "x-apisports-key": API_KEY
}

# Fetch next fixtures for Chelsea
url = f"https://v3.football.api-sports.io/fixtures?team={TEAM_ID}&season={SEASON}&next={LIMIT}"
res = requests.get(url, headers=headers)
data = res.json().get("response", [])

# Process fixtures
fixtures = []
for f in data:
    fixture_date = f["fixture"]["date"]
    date = isoparse(fixture_date)
    fixtures.append({
        "date": date.strftime("%Y-%m-%d"),
        "time": date.strftime("%H:%M"),
        "opponent": (
            f["teams"]["away"]["name"] if f["teams"]["home"]["id"] == TEAM_ID else f["teams"]["home"]["name"]
        ),
        "venue": "Home" if f["teams"]["home"]["id"] == TEAM_ID else "Away",
        "competition": f["league"]["name"],
        "logo": f["league"]["logo"],
        "team_logo": f["teams"]["away"]["logo"] if f["teams"]["home"]["id"] == TEAM_ID else f["teams"]["home"]["logo"]
    })

# Save to JSON file
output_path = "DATA/fixtures.json"
with open(output_path, "w") as f:
    json.dump(fixtures, f, indent=4)

print(f"✅ Saved {len(fixtures)} fixtures to {output_path}")