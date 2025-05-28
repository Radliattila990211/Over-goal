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
        return response.json().get("response", [])
    else:
        st.error(f"API hiba: {response.status_code}")
        return []

@st.cache_data(ttl=30)
def get_stats(fixture_id):
    url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures/statistics?fixture={fixture_id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("response", [])
    return []

def calculate_signals(match, stats):
    signals = []
    elapsed = match["fixture"]["status"].get("elapsed", 0)
    goals_home = match["goals"]["home"] or 0
    goals_away = match["goals"]["away"] or 0

    home_stats = {stat["type"]: stat["value"] for stat in stats[0]["statistics"]} if len(stats) > 0 else {}
    away_stats = {stat["type"]: stat["value"] for stat in stats[1]["statistics"]} if len(stats) > 1 else {}
    shots_on_target = (home_stats.get("Shots on Goal") or 0) + (away_stats.get("Shots on Goal") or 0)

    if elapsed <= 15 and shots_on_target >= 3 and goals_home + goals_away == 0:
        signals.append("félidő 0,5 over")

    if elapsed <= 30 and shots_on_target >= 4:
        signals.append("félidő 0,5 over ++")

    if elapsed >= 60 and abs(goals_home - goals_away) == 1:
        signals.append("még egy gól")

    return signals

st.title("⚽ Élő Foci Stratégiák – Frissített Logika")

live_matches = get_live_fixtures()
st.write(f"Élő meccsek száma: {len(live_matches)}")

for match in live_matches:
    fixture_id = match["fixture"]["id"]
    teams = f"{match['teams']['home']['name']} vs {match['teams']['away']['name']}"
    time = match["fixture"]["status"]["elapsed"]
    goals = f"{match['goals']['home']} - {match['goals']['away']}"

    stats = get_stats(fixture_id)
    signals = calculate_signals(match, stats)

    with st.expander(f"{teams} | {time}' | Eredmény: {goals}"):
        st.write(f"Meccs ID: {fixture_id}")
        st.write("Jelzések:", ", ".join(signals) if signals else "Nincs jelzés")
        if stats:
            home_sog = next((x["value"] for x in stats[0]["statistics"] if x["type"] == "Shots on Goal"), 0)
            away_sog = next((x["value"] for x in stats[1]["statistics"] if x["type"] == "Shots on Goal"), 0)
            st.write("Kapura lövések (összesen):", home_sog + away_sog)
        else:
            st.write("⚠️ Statisztikák nem érhetők el ehhez a meccshez.")
