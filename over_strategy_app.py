import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Élő Foci Fogadás Stratégiák", layout="wide")

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

def get_stat_value(stats_list, stat_name):
    # Segédfüggvény az adott stat értékének kinyeréséhez egy csapat statisztikáiból
    for stat in stats_list:
        if stat['type'] == stat_name:
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

    # Kaput eltaláló lövések (Shots on Goal)
    shots_on_target_home = get_stat_value(home_stats, 'Shots on Goal')
    shots_on_target_away = get_stat_value(away_stats, 'Shots on Goal')
    total_shots_on_target = shots_on_target_home + shots_on_target_away

    signals = []

    # 1. Félidő 0,5 over: az első 15 percben 3 kaput eltaláló lövés és nincs gól
    if elapsed <= 15:
        if total_shots_on_target >= 3 and (goals_home + goals_away) == 0:
            signals.append("félidő 0,5 over")

    # 2. 0,5 over ++: a 25. percben legalább 4 kaput eltaláló lövés
    if 24 <= elapsed <= 26:
        if total_shots_on_target >= 4:
            signals.append("0,5 over ++")

    # 3. Még egy gól: a 60. percben egyik csapat 1 góllal vezet
    if 59 <= elapsed <= 61:
        if abs(goals_home - goals_away) == 1 and (goals_home != goals_away):
            signals.append("még egy gól")

    if signals:
        return signals
    else:
        return None

def main():
    st.title("⚽ Élő Foci Fogadási Stratégiák")
    st.write("Jelzések az élő meccsek alapján az előre megadott feltételekre.")

    fixtures = get_live_fixtures()

    if not fixtures:
        st.info("Jelenleg nincs élő mérkőzés.")
        return

    for fixture in fixtures:
        home_team = fixture['teams']['home']['name']
        away_team = fixture['teams']['away']['name']
        league_name = fixture['league']['name']
        elapsed = fixture['fixture']['status']['elapsed'] or 0
        status_long = fixture['fixture']['status']['long']

        signals = analyze_fixture(fixture)

        st.markdown(f"### {home_team} vs {away_team}  — {league_name}")
        st.write(f"**Állás:** {fixture['goals']['home']} : {fixture['goals']['away']}  |  **Állapot:** {status_long} ({elapsed} perc)")

        if signals:
            for sig in signals:
                st.success(f"**Jelzés:** {sig}")
        else:
            st.write("Nincs jelzés a megadott feltételek alapján.")

        st.divider()

if __name__ == "__main__":
    main()
