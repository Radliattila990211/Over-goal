import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Élő Foci Stratégiák", layout="wide")

API_KEY = "fe42fb2bd6d9cbd944bd3533bb53b82f"  # Hivatalos API-Football kulcs
headers = {
    "x-apisports-key": API_KEY
}

@st.cache_data(ttl=30)
def get_live_fixtures():
    url = "https://v3.football.api-sports.io/fixtures?live=all"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('response', [])
    else:
        st.error(f"Hiba az API hívásban: {response.status_code}")
        return []

@st.cache_data(ttl=30)
def get_stats(fixture_id):
    url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('response', [])
    else:
        return []

def check_signals(fixture):
    fixture_id = fixture['fixture']['id']
    elapsed = fixture['fixture']['status']['elapsed']
    goals_home = fixture['goals']['home']
    goals_away = fixture['goals']['away']
    stats = get_stats(fixture_id)

    if len(stats) < 2:
        return []

    home_stats = {stat['type']: stat['value'] for stat in stats[0].get('statistics', [])}
    away_stats = {stat['type']: stat['value'] for stat in stats[1].get('statistics', [])}

    shots_on_target = (home_stats.get('Shots on Goal') or 0) + (away_stats.get('Shots on Goal') or 0)
    total_goals = (goals_home or 0) + (goals_away or 0)
    signal_list = []

    # Félidő 0.5 Over
    if elapsed is not None and elapsed <= 15 and shots_on_target >= 3 and total_goals == 0:
        signal_list.append("Félidő 0.5 Over")

    # 0.5 Over ++
    if elapsed is not None and elapsed <= 30 and shots_on_target >= 4:
        signal_list.append("0.5 Over ++")

    # Lesz még egy gól
    if elapsed is not None and elapsed >= 60 and abs((goals_home or 0) - (goals_away or 0)) == 1:
        signal_list.append("Lesz még egy gól")

    return signal_list

# Oldal megjelenítés
st.title("⚽ Élő Foci Stratégiák")
live_matches = get_live_fixtures()
st.subheader(f"Élő mérkőzések száma: {len(live_matches)}")

if not live_matches:
    st.warning("Nincs élő mérkőzés jelenleg.")
else:
    for fixture in live_matches:
        teams = f"{fixture['teams']['home']['name']} vs {fixture['teams']['away']['name']}"
        elapsed = fixture['fixture']['status']['elapsed']
        st.markdown(f"### {teams} - {elapsed}'")

        signals = check_signals(fixture)

        if signals:
            for signal in signals:
                st.success(f"✅ {signal}")
        else:
            st.info("Nincs jelzés jelenleg.")
