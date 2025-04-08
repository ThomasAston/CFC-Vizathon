import requests

API_KEY = "1f640d32af86dbe571abc0cc153a9e0b"  # Replace with your actual API key

headers = {
    "x-apisports-key": API_KEY
}

# Specify the season
season = 2023  # Replace with the desired season

# Search for teams with "Chelsea" in the name
query = "chelsea"
teams_url = f"https://v3.football.api-sports.io/teams?search={query}"

teams_response = requests.get(teams_url, headers=headers)

if teams_response.status_code == 200:
    teams = teams_response.json()["response"]
    print(f"Found {len(teams)} team(s) matching '{query}':\n")
    for team in teams:
        info = team["team"]
        team_id = info["id"]
        print(f"- {info['name']} (ID: {team_id})")

        # Fetch leagues for the team in the given season
        leagues_url = f"https://v3.football.api-sports.io/leagues?team={team_id}&season={season}"
        leagues_response = requests.get(leagues_url, headers=headers)

        if leagues_response.status_code == 200:
            leagues = leagues_response.json()["response"]
            league_names = [league["league"]["name"] for league in leagues]
            league_ids = [league["league"]["id"] for league in leagues]
            print(f"  Leagues in {season}: {', '.join(league_names)} (ID: {', '.join(map(str, league_ids))})")
        else:
            print(f"  Failed to fetch leagues for team ID {team_id} in season {season}: {leagues_response.status_code}")
else:
    print(f"Failed to fetch teams: {teams_response.status_code}")