import streamlit as st
import requests
import os

st.set_page_config(page_title="Foci Over stratégia élőben", layout="wide")

# API kulcs a Streamlit Cloud secretsből
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

def evaluate_over_criteria(stats, elapsed):
    home_stats = {stat['type']: stat['value'] for stat in stats[0]['statistics']} if len(stats) > 0 else {}
    away_stats = {stat['type']: stat['value'] for stat in stats[1]['statistics']} if len(stats) > 1 else {}

    total_shots = home_stats.get('Shots total', 0) + away_stats.get('Shots total', 0)
    shots_on_target = home_stats.get('Shots on Goal', 0) + away_stats.get('Shots on Goal', 0)
    corners = home_stats.get('Corners', 0) + away_stats.get('Corners', 0)
    dangerous_attacks = home_stats.get('Dangerous Attacks', 0) + away_stats.get('Dangerous Attacks', 0)

    over_05 = total_shots >= 5 or shots_on_target >= 2 or corners >= 3
    over_15 = (elapsed >= 25 and total_shots >= 10 and shots_on_target >= 4) or (elapsed >= 60 and total_shots >= 5)
    over_25 = elapsed <= 35 and total_shots >= 15 and shots_on_target >= 6 and corners >= 5 and dangerous_attacks >= 40

    return over_05, over_15, over_25

st.title("⚽ Élő Foci Over Gól Stratégiák")

fixtures = get_live_fixtures()

if not fixtures:
    st.info("Jelenleg nincs élő mérkőzés vagy probléma az adatlekéréssel.")
else:
    for match in fixtures:
        fixture_id = match['fixture']['id']
        home = match['teams']['home']['name']
        away = match['teams']['away']['name']
        goals_home = match['goals']['home']
        goals_away = match['goals']['away']
        elapsed = match['fixture']['status']['elapsed'] or 0

        stats = get_stats(fixture_id)

        over_05, over_15, over_25 = evaluate_over_criteria(stats, elapsed)

        col1, col2 = st.columns([3,1])
        with col1:
            st.markdown(f"### {home} vs {away}  — {goals_home} : {goals_away}  ({elapsed}′)")
        with col2:
            st.markdown(
                f"**Over 0.5:** {'✅' if over_05 else '❌'}  \n"
                f"**Over 1.5:** {'✅' if over_15 else '❌'}  \n"
                f"**Over 2.5:** {'✅' if over_25 else '❌'}"
            )
        with st.expander("Részletes statisztikák"):
            if stats:
                for side in stats:
                    team = side['team']['name']
                    st.markdown(f"#### {team}")
                    for stat in side['statistics']:
                        st.write(f"{stat['type']}: {stat['value']}")
            else:
                st.write("Nincsenek elérhető statisztikák.")

        st.markdown("---")
