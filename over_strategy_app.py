import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Élő Foci Stratégiák", layout="wide")

API_KEY = st.secrets["API_KEY"]

headers = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

@st.cache_data(ttl=30)
def get_live_fixtures():
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures?live=all"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('response', [])
    else:
        st.error(f"Hiba az API hívásban: {response.status_code}")
        return []

@st.cache_data(ttl=3600)
def get_today_fixtures():
    today = datetime.today().strftime("%Y-%m-%d")
    url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures?date={today}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("response", [])
    else:
        st.error(f"Fixture lekérési hiba: {response.status_code}")
        return []

@st.cache_data(ttl=3600)
def get_team_stats(team_id, league_id, season):
    url = f"https://api-football-v1.p.rapidapi.com/v3/teams/statistics?team={team_id}&league={league_id}&season={season}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("response", {})
    else:
        return {}

@st.cache_data(ttl=30)
def get_stats(fixture_id):
    url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures/statistics?fixture={fixture_id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('response', [])
    else:
        return []

def evaluate_over_criteria(stats, elapsed, goals_home, goals_away):
    try:
        home_stats = {stat['type']: stat['value'] for stat in stats[0]['statistics']} if len(stats) > 0 else {}
        away_stats = {stat['type']: stat['value'] for stat in stats[1]['statistics']} if len(stats) > 1 else {}
    except:
        return False, False, False, False, False

    shots_on_target = (home_stats.get('Shots on Goal') or 0) + (away_stats.get('Shots on Goal') or 0)

    over_05 = shots_on_target > 5
    over_15 = shots_on_target > 8
    over_25 = shots_on_target > 10
    half_time_05 = (15 <= elapsed <= 45) and shots_on_target >= 2
    plus_one_goal = elapsed >= 75 and abs((goals_home or 0) - (goals_away or 0)) == 1

    return over_05, over_15, over_25, half_time_05, plus_one_goal

def evaluate_pre_match(fixtures):
    suggestions = []
    for match in fixtures:
        try:
            home_team = match['teams']['home']
            away_team = match['teams']['away']
            league_id = match['league']['id']
            season = match['league']['season']

            home_stats = get_team_stats(home_team['id'], league_id, season)
            away_stats = get_team_stats(away_team['id'], league_id, season)

            home_goals_avg = home_stats.get("goals", {}).get("for", {}).get("average", {}).get("total", 0)
            away_goals_avg = away_stats.get("goals", {}).get("for", {}).get("average", {}).get("total", 0)

            if home_goals_avg and away_goals_avg:
                if float(home_goals_avg) >= 2.5 and float(away_goals_avg) >= 2.5:
                    suggestions.append({
                        "home": home_team["name"],
                        "away": away_team["name"],
                        "home_avg": home_goals_avg,
                        "away_avg": away_goals_avg,
                        "league": match['league']['name'],
                        "time": match['fixture']['date']
                    })
        except Exception as e:
            continue
    return suggestions

# TAB STRUKTÚRA
tabs = st.tabs(["Élő Foci Stratégiák", "Meccs előtti ajánlások"])

# ÉLŐ FOCI
with tabs[0]:
    st.header("⚽ Élő Foci |oai:code-citation|
