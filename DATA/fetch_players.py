import requests
import json
from collections import defaultdict
from time import sleep

API_KEY = "1f640d32af86dbe571abc0cc153a9e0b"  # Replace with your actual API key
SEASON = 2023

headers = {
    "x-apisports-key": API_KEY
}

# Map squad names to their API-Football team IDs
squad_team_ids = {
    "Senior Men": 49,     # Chelsea FC
    "Senior Women": 1853,
    "U21s Men": 7192,
    "U18s Men": 15391
}

radar_fields = {
    "Goalkeeper": {
        "Saves": ("goals", "saves"),
        "Conceded": ("goals", "conceded"),
        "Passes": ("passes", "total"),
        "Av. Rating": ("games", "rating")
    },
    "Defender": {
        "Tackles": ("tackles", "total"),
        "Interceptions": ("tackles", "interceptions"),
        "Blocks": ("tackles", "blocks"),
        "Duels": ("duels", "total"),
        "Duels Won": ("duels", "won"),
        "Av. Rating": ("games", "rating")
    },
    "Midfielder": {
        "Passes": ("passes", "total"),
        "Key Passes": ("passes", "key"),
        "Pass Accuracy": ("passes", "accuracy"),
        "Assists": ("goals", "assists"),
        "Dribble Success": ("dribbles", "success"), 
        "Av. Rating": ("games", "rating")
    },
    "Attacker": {
        "Goals": ("goals", "total"),
        "Assists": ("goals", "assists"),
        "Attempts": ("shots", "total"),
        "On Target Attempts": ("shots", "on"),
        "Dribble Success": ("dribbles", "success"), 
        "Av. Rating": ("games", "rating")
    }
}


# Get competitions a team participates in
def get_team_leagues(team_id):
    print(f"🔍 Fetching leagues for team ID {team_id}")
    url = f"https://v3.football.api-sports.io/leagues?team={team_id}&season={SEASON}"
    res = requests.get(url, headers=headers)
    leagues = res.json().get("response", [])
    print(f"Found {len(leagues)} leagues for team ID {team_id}")
    return [
        {
            "league_id": l["league"]["id"],
            "league_name": l["league"]["name"]
        }
        for l in leagues
        if l["league"]["name"].lower() != "friendlies clubs"
    ]

# Get all teams in a given competition
def get_teams_in_league(league_id):
    print(f"📋 Fetching teams in league ID {league_id}")
    url = f"https://v3.football.api-sports.io/teams?league={league_id}&season={SEASON}"
    res = requests.get(url, headers=headers)
    teams = res.json().get("response", [])
    return [
        {
            "team_id": t["team"]["id"],
            "team_name": t["team"]["name"]
        }
        for t in teams
    ]

# Fetch and rank players by most appearances
def get_top_players(team_id, limit=20):
    print(f"👥 Fetching players for team ID {team_id}")
    all_players = []
    page = 1
    while True:
        url = f"https://v3.football.api-sports.io/players?team={team_id}&season={SEASON}&page={page}"
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            print(f"❌ Failed to fetch team {team_id}: {res.status_code}")
            break
        response = res.json().get("response", [])
        if not response:
            break
        all_players.extend(response)
        page += 1

    if not all_players:
        return []

    players_sorted = sorted(
        all_players,
        key=lambda x: x["statistics"][0]["games"].get("appearences") or 0,
        reverse=True
    )

    result = []
    for p in players_sorted[:limit]:
        
        stats = p["statistics"][0]
        available_stats = set()
        for category in stats.values():
            if isinstance(category, dict):
                available_stats.update(category.keys())
        
        position = stats["games"].get("position") or "Unknown"
        
        # Safely get minutes
        minutes_played = stats.get("games", {}).get("minutes") or 0

        radar_vals = {}
        field_map = radar_fields.get(position, {})

        for stat_name, (section, key) in field_map.items():
            raw_value = stats.get(section, {}).get(key)
            
            if raw_value is None:
                radar_vals[stat_name] = 0
                continue

            # Convert rating from string to float
            if stat_name == "Av. Rating":
                radar_vals[stat_name] = round(float(raw_value), 2)
            else:
                radar_vals[stat_name] = raw_value

        result.append({
            "id": p["player"]["id"],
            "name": p["player"]["name"],
            "age": p["player"]["age"],
            "height": p["player"]["height"],
            "weight": p["player"]["weight"],
            "nationality": p["player"]["nationality"],
            "photo": p["player"]["photo"],
            "position": position,
            "appearances": stats["games"].get("appearences", 0),
            "minutes": minutes_played,
            "radar": radar_vals
        })

    return result

# Main collection logic
all_data = {"chelsea_squads": {}, "opposition": defaultdict(lambda: defaultdict(dict))}

for squad_name, team_id in squad_team_ids.items():
    print(f"=== Processing {squad_name} squad ===")

    # Store Chelsea players
    all_data["chelsea_squads"][squad_name] = get_top_players(team_id)

    leagues = get_team_leagues(team_id)[:2]

    for league in leagues:
        league_id = league["league_id"]
        league_name = league["league_name"]

        teams = get_teams_in_league(league_id)
        selected = [t for t in teams if t["team_id"] != team_id][:5]

        for team in selected:
            team_id = team["team_id"]
            team_name = team["team_name"]
            players = get_top_players(team_id)
            all_data["opposition"][squad_name][league_name][team_name] = players

# Save output
def convert(obj):
    if isinstance(obj, defaultdict):
        obj = {k: convert(v) for k, v in obj.items()}
    return obj

with open("DATA/players.json", "w") as f:
    json.dump(convert(all_data), f, indent=4)

print("✅ Data collection complete. Saved to players.json")
