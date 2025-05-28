import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="⚽ Élő Foci Stratégiák", layout="wide")

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
        return response.json().get('response', []), 200
    else:
        return [], response.status_code

@st.cache_data(ttl=30)
def get_stats(fixture_id):
    url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures/statistics?fixture={fixture_id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("response", [])
    else:
        return []

def analyze_match(fixture):
    fixture_id = fixture["fixture"]["id"]
    elapsed = fixture["fixture"]["status"].get("elapsed", 0)
    goals_home = fixture["goals"]["home"]
    goals_away = fixture["goals"]["away"]

    stats = get_stats(fixture_id)

    if not stats or len(stats) < 2:
        return None, f"Nincs statisztika: fixture ID {fixture_id}"

    try:
        home_stats = {stat["type"]: stat["value"] for stat in stats[0]["statistics"]}
        away_stats = {stat["type"]: stat["value"] for stat in stats[1]["statistics"]}
        shots_on_target = (home_stats.get("Shots on Goal") or 0) + (away_stats.get("Shots on Goal") or 0)
    except Exception as e:
        return None, f"Hiba stat feldolgozáskor: {e}"

    if elapsed <= 15 and shots_on_target >= 3 and (goals_home + goals_away) == 0:
        return "Félidő 0.5 Over", None
    elif elapsed <= 30 and shots_on_target >= 4:
        return "0.5 Over ++", None
    elif elapsed >= 60 and abs(goals_home - goals_away) == 1:
        return "Lesz még egy gól", None
    else:
        return None, f"Nem felel meg: {elapsed} perc, {shots_on_target} kapura lövés"

st.title("⚽ Élő Foci Stratégiák")

fixtures, status_code = get_live_fixtures()
st.subheader(f"API státusz: {status_code}")

if status_code != 200:
    st.error("Hiba az élő meccsek lekérésekor.")
    st.stop()

if not fixtures:
    st.warning("Jelenleg nincs élő meccs.")
else:
    for fixture in fixtures:
        home = fixture["teams"]["home"]["name"]
        away = fixture["teams"]["away"]["name"]
        time = fixture["fixture"]["status"].get("elapsed", 0)
        score = f"{fixture['goals']['home']} - {fixture['goals']['away']}"
        st.markdown(f"### {home} vs {away} ({score}) - {time}'")

        jelzes, debug_msg = analyze_match(fixture)

        if jelzes:
            st.success(f"💡 **Jelzés:** {jelzes}")
        else:
            st.info(debug_msg)
