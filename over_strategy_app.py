import streamlit as st
import requests
from datetime import datetime

# Streamlit oldal beállítás
st.set_page_config(page_title="Élő Foci Stratégiák", layout="wide")
st.title("⚽ Élő Foci Stratégiák")

API_KEY = "fe42fb2bd6d9cbd944bd3533bb53b82f"

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

@st.cache_data(ttl=30)
def get_stats(fixture_id):
    url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures/statistics?fixture={fixture_id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('response', [])
    return []

def extract_shots_on_target(stats):
    try:
        home_stats = {s['type']: s['value'] for s in stats[0]['statistics']}
        away_stats = {s['type']: s['value'] for s in stats[1]['statistics']}
        shots_on_target = home_stats.get('Shots on Goal', 0) + away_stats.get('Shots on Goal', 0)
        return shots_on_target
    except:
        return 0

def evaluate_signals(fixture, stats):
    events = []
    fixture_id = fixture['fixture']['id']
    elapsed = fixture['fixture']['status']['elapsed']
    goals_home = fixture['goals']['home'] or 0
    goals_away = fixture['goals']['away'] or 0
    total_goals = goals_home + goals_away

    shots_on_target = extract_shots_on_target(stats)

    # Jelzések
    if elapsed <= 15 and total_goals == 0 and shots_on_target >= 3:
        events.append("Félidő 0.5 Over")
    if elapsed <= 30 and shots_on_target >= 4:
        events.append("0.5 Over ++")
    if elapsed >= 60 and abs(goals_home - goals_away) == 1:
        events.append("Lesz még egy gól")

    return events

# Fő program
fixtures = get_live_fixtures()

if not fixtures:
    st.warning("Nincsenek élő mérkőzések.")
else:
    for match in fixtures:
        fixture_id = match['fixture']['id']
        stats = get_stats(fixture_id)
        if not stats:
            continue

        signals = evaluate_signals(match, stats)
        if signals:
            home = match['teams']['home']['name']
            away = match['teams']['away']['name']
            elapsed = match['fixture']['status']['elapsed']
            goals = f"{match['goals']['home']} - {match['goals']['away']}"
            st.markdown(f"### ⚠️ {home} vs {away} ({elapsed}' - {goals})")
            for signal in signals:
                st.success(f"💡 Jelzés: {signal}")
