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
def get_stats(fixture_id):
    url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures/statistics?fixture={fixture_id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('response', [])
    else:
        return []

def check_shots_on_target(stats):
    # A statisztikák listája csapatokra bontva
    if len(stats) < 2:
        return 0, 0  # ha nincs adat
    try:
        home_stats = {item['type']: item['value'] for item in stats[0]['statistics']}
        away_stats = {item['type']: item['value'] for item in stats[1]['statistics']}
        shots_home = home_stats.get('Shots on Goal') or 0
        shots_away = away_stats.get('Shots on Goal') or 0
        return shots_home, shots_away
    except Exception:
        return 0, 0

def live_signals(fixtures):
    signals = []
    for match in fixtures:
        fixture = match['fixture']
        score = match['score']
        elapsed = fixture.get('status', {}).get('elapsed', 0)
        goals_home = score.get('fulltime', {}).get('home') or score.get('halftime', {}).get('home') or 0
        goals_away = score.get('fulltime', {}).get('away') or score.get('halftime', {}).get('away') or 0
        fixture_id = fixture['id']

        stats = get_stats(fixture_id)
        shots_home, shots_away = check_shots_on_target(stats)
        total_shots = shots_home + shots_away

        # 1. Félidő 0,5 over: első 15 perc, legalább 3 kaput eltaláló lövés, de nincs gól
        if elapsed <= 15 and total_shots >= 3 and (goals_home + goals_away) == 0:
            signals.append({
                "fixture": f"{match['teams']['home']['name']} - {match['teams']['away']['name']}",
                "signal": "Félidő 0,5 over",
                "elapsed": elapsed,
                "shots": total_shots,
                "goals": goals_home + goals_away
            })

        # 2. 0,5 over ++ : a 25. percben legalább 4 kaput eltaláló lövés
        if elapsed == 25 and total_shots >= 4:
            signals.append({
                "fixture": f"{match['teams']['home']['name']} - {match['teams']['away']['name']}",
                "signal": "0,5 over ++",
                "elapsed": elapsed,
                "shots": total_shots,
                "goals": goals_home + goals_away
            })

        # 3. Még egy gól : 60. percben az egyik csapat 1 góllal vezet
        if elapsed == 60 and abs(goals_home - goals_away) == 1:
            signals.append({
                "fixture": f"{match['teams']['home']['name']} - {match['teams']['away']['name']}",
                "signal": "Még egy gól",
                "elapsed": elapsed,
                "score": f"{goals_home}-{goals_away}"
            })

    return signals

# UI

st.title("⚽ Élő Foci Stratégiák")

live_fixtures = get_live_fixtures()

if not live_fixtures:
    st.info("Jelenleg nincs élő mérkőzés.")
else:
    st.subheader("Élő mérkőzések és jelzések")
    signals = live_signals(live_fixtures)

    if signals:
        for s in signals:
            st.markdown(f"**{s['fixture']}**  -  _{s['signal']}_ (perc: {s['elapsed']})")
            if 'shots' in s:
                st.write(f"Kapura lövések összesen: {s['shots']}, Gólok: {s.get('goals', 'N/A')}")
            if 'score' in s:
                st.write(f"Eredmény: {s['score']}")
    else:
        st.info("Jelenleg nincs jelzés az élő meccseken.")
