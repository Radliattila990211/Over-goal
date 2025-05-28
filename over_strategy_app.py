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

@st.cache_data(ttl=30)
def get_fixture_stats(fixture_id):
    url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures/statistics?fixture={fixture_id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('response', [])
    else:
        return []

def get_stat_value(stats_list, stat_type):
    for stat in stats_list:
        if stat['type'] == stat_type:
            return stat['value'] if stat['value'] is not None else 0
    return 0

def analyze_fixture(fixture):
    fixture_id = fixture['fixture']['id']
    elapsed = fixture['fixture']['status']['elapsed'] or 0
    goals_home = fixture['goals']['home'] or 0
    goals_away = fixture['goals']['away'] or 0

    stats = get_fixture_stats(fixture_id)
    if len(stats) < 2:
        return None

    home_stats = stats[0].get('statistics', [])
    away_stats = stats[1].get('statistics', [])

    shots_on_target_home = get_stat_value(home_stats, 'Shots on Goal')
    shots_on_target_away = get_stat_value(away_stats, 'Shots on Goal')
    total_shots_on_target = shots_on_target_home + shots_on_target_away

    signals = []

    # 1. Félidő 0,5 over: 15. percig 3 kaput eltaláló lövés és nincs gól
    if elapsed <= 15:
        if total_shots_on_target >= 3 and (goals_home + goals_away) == 0:
            signals.append("félidő 0,5 over")

    # 2. Félidő 0,5 over ++: 30. percig legalább 4 kaput eltaláló lövés
    if elapsed <= 30:
        if total_shots_on_target >= 4:
            signals.append("félidő 0,5 over ++")

    # 3. Még egy gól: 60. percben 1 gólos különbség
    if 59 <= elapsed <= 61:
        if abs(goals_home - goals_away) == 1:
            signals.append("még egy gól")

    return signals if signals else None

# Streamlit megjelenítés
st.title("⚽ Élő Foci Stratégiák")

live_fixtures = get_live_fixtures()

if not live_fixtures:
    st.info("Nincsenek jelenleg élő mérkőzések.")
else:
    for fixture in live_fixtures:
        league_name = fixture['league']['name']
        home_team = fixture['teams']['home']['name']
        away_team = fixture['teams']['away']['name']
        elapsed = fixture['fixture']['status']['elapsed'] or 0
        score_home = fixture['goals']['home'] or 0
        score_away = fixture['goals']['away'] or 0
        venue = fixture['fixture']['venue']['name'] if fixture['fixture']['venue'] else "N/A"

        signals = analyze_fixture(fixture)

        st.markdown(f"### {league_name} — {home_team} vs {away_team}")
        st.write(f"**Idő:** {elapsed} perc")
        st.write(f"**Helyszín:** {venue}")
        st.write(f"**Eredmény:** {score_home} - {score_away}")

        if signals:
            st.success(f"📢 Jelzések: {', '.join(signals)}")
        else:
            st.write("Nincs aktuális jelzés.")

        st.markdown("---")
