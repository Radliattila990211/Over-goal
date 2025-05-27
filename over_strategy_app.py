import streamlit as st
import requests

st.set_page_config(page_title="Élő Sport Stratégiák", layout="wide")

API_KEY = st.secrets["API_KEY"]

# Foci API beállítás
football_headers = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

# Tenisz API beállítás (példa, RapidAPI sports-tennis)
tennis_headers = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "api-tennis-v1.p.rapidapi.com"
}

@st.cache_data(ttl=30)
def get_live_football_fixtures():
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures?live=all"
    response = requests.get(url, headers=football_headers)
    if response.status_code == 200:
        return response.json().get('response', [])
    else:
        st.error(f"Foci API hiba: {response.status_code}")
        return []

@st.cache_data(ttl=30)
def get_football_stats(fixture_id):
    url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures/statistics?fixture={fixture_id}"
    response = requests.get(url, headers=football_headers)
    if response.status_code == 200:
        return response.json().get('response', [])
    else:
        return []

@st.cache_data(ttl=30)
def get_live_tennis_fixtures():
    url = "https://api-tennis-v1.p.rapidapi.com/matches/live"
    response = requests.get(url, headers=tennis_headers)
    if response.status_code == 200:
        return response.json().get('matches', [])
    else:
        st.error(f"Tenisz API hiba: {response.status_code}")
        return []

def evaluate_football_criteria(stats, elapsed, goals_home, goals_away):
    home_stats = {stat['type']: stat['value'] for stat in stats[0]['statistics']} if len(stats) > 0 else {}
    away_stats = {stat['type']: stat['value'] for stat in stats[1]['statistics']} if len(stats) > 1 else {}

    shots_on_target = home_stats.get('Shots on Goal', 0) + away_stats.get('Shots on Goal', 0)

    over_05 = shots_on_target > 5
    over_15 = shots_on_target > 8
    over_25 = shots_on_target > 10
    half_time_05 = (elapsed >= 15 and elapsed <= 45) and (shots_on_target >= 2)

    plus_one_goal = False
    if elapsed >= 75:
        goal_diff = abs((goals_home or 0) - (goals_away or 0))
        if goal_diff == 1:
            plus_one_goal = True

    return over_05, over_15, over_25, half_time_05, plus_one_goal

def tennis_set_over_under_9_5(current_set_score):
    try:
        games = current_set_score.split('-')
        if len(games) != 2:
            return None  # Nem értelmezhető
        home_games = int(games[0])
        away_games = int(games[1])
        # Over 9.5 ha 3-2, 2-3 vagy 3-3 az állás
        if (home_games == 3 and away_games in [2, 3]) or (away_games == 3 and home_games in [2, 3]):
            return "Over 9.5 ✅"
        # Under 9.5 ha 3-0 vagy 0-3
        elif (home_games == 3 and away_games == 0) or (away_games == 3 and home_games == 0):
            return "Under 9.5 ✅"
        else:
            return "Nincs jelzés ❌"
    except:
        return "Nincs jelzés ❌"

st.title("⚽⚾ Élő Sport Fogadási Stratégiák")

tab = st.tabs(["Foci", "Tenisz"])

with tab[0]:
    st.header("Foci Over Gól Stratégiák")
    fixtures = get_live_football_fixtures()
    if not fixtures:
        st.info("Jelenleg nincs élő focimeccs vagy probléma az adatlekéréssel.")
    else:
        for match in fixtures:
            fixture_id = match['fixture']['id']
            home = match['teams']['home']['name']
            away = match['teams']['away']['name']
            goals_home = match['goals']['home']
            goals_away = match['goals']['away']
            elapsed = match['fixture']['status']['elapsed'] or 0

            stats = get_football_stats(fixture_id)

            over_05, over_15, over_25, half_time_05, plus_one_goal = evaluate_football_criteria(stats, elapsed, goals_home, goals_away)

            col1, col2 = st.columns([3,1])
            with col1:
                st.markdown(f"### {home} vs {away}  — {goals_home} : {goals_away}  ({elapsed}′)")
            with col2:
                st.markdown(
                    f"**Over 0.5:** {'✅' if over_05 else '❌'}  \n"
                    f"**Over 1.5:** {'✅' if over_15 else '❌'}  \n"
                    f"**Over 2.5:** {'✅' if over_25 else '❌'}  \n"
                    f"**Félidő 0.5+:** {'✅' if half_time_05 else '❌'}  \n"
                    f"**75+ more 1 goal:** {'✅' if plus_one_goal else '❌'}"
                )
            with st.expander("Részletes statisztikák"):
                if stats:
                    for side in stats:
                        team = side['team']['name']
                        st.markdown(f"#### {team}")
                        for stat in side['statistics']:
                            st.write(f"{stat['type']}: {stat['value']}")

with tab[1]:
    st.header("Tenisz Over/Under 9.5 Szett Stratégia")
    tennis_matches = get_live_tennis_fixtures()
    if not tennis_matches:
        st.info("Jelenleg nincs élő teniszmérkőzés vagy probléma az adatlekéréssel.")
    else:
        for match in tennis_matches:
            home = match.get('home', {}).get('name', 'Ismeretlen')
            away = match.get('away', {}).get('name', 'Ismeretlen')
            current_set_score = match.get('scores', {}).get('current_set', "0-0")  # ezt az API-tól kell igazítani

            signal = tennis_set_over_under_9_5(current_set_score)

            st.markdown(f"### {home} vs {away}")
            st.markdown(f"Jelenlegi szett állás: **{current_set_score}**")
            st.markdown(f"Jelzés: **{signal}**")
