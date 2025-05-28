import streamlit as st
import requests
from datetime import datetime, timezone

st.set_page_config(page_title="Élő Foci Stratégiák", layout="wide")

API_KEY = "fe42fb2bd6d9cbd944bd3533bb53b82f"

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
def get_fixture_stats(fixture_id):
    url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('response', [])
    else:
        return []

def analyze_live_match(fixture):
    fixture_id = fixture['fixture']['id']
    elapsed = fixture['fixture']['status']['elapsed'] or 0
    goals_home = fixture['goals']['home']
    goals_away = fixture['goals']['away']
    stats = get_fixture_stats(fixture_id)

    if not stats or len(stats) < 2:
        return None

    try:
        home_stats = {stat['type']: stat['value'] for stat in stats[0]['statistics']}
        away_stats = {stat['type']: stat['value'] for stat in stats[1]['statistics']}
    except Exception:
        return None

    shots_on_target = (home_stats.get('Shots on Goal') or 0) + (away_stats.get('Shots on Goal') or 0)

    # Jelzésfeltételek
    if elapsed <= 15 and (goals_home == 0 and goals_away == 0) and shots_on_target >= 3:
        return {"signal": "Félidő 0,5 Over", "elapsed": elapsed, "shots_on_target": shots_on_target}

    if elapsed <= 30 and shots_on_target >= 4:
        return {"signal": "Félidő 0,5 Over ++", "elapsed": elapsed, "shots_on_target": shots_on_target}

    if elapsed >= 60 and abs((goals_home or 0) - (goals_away or 0)) == 1:
        return {"signal": "Még egy gól", "elapsed": elapsed, "goals_home": goals_home, "goals_away": goals_away}

    return None

def main():
    st.title("⚽ Élő Foci Stratégiák")

    fixtures = get_live_fixtures()
    st.write(f"Élő meccsek száma: {len(fixtures)}")

    if not fixtures:
        st.info("Jelenleg nincs élő futballmérkőzés.")
        return

    # Jelzések megjelenítése
    signals = []
    for fixture in fixtures:
        signal = analyze_live_match(fixture)
        if signal:
            signals.append({
                "league": fixture['league']['name'],
                "home": fixture['teams']['home']['name'],
                "away": fixture['teams']['away']['name'],
                "elapsed": signal.get("elapsed"),
                "signal": signal.get("signal"),
                "shots_on_target": signal.get("shots_on_target", "N/A"),
                "score": f"{fixture['goals']['home']} - {fixture['goals']['away']}"
            })

    if signals:
        st.subheader("Jelzések élő meccsekhez:")
        for s in signals:
            st.markdown(f"**{s['league']}**: {s['home']} - {s['away']} ({s['elapsed']} perc)  \n"
                        f"Jelzés: {s['signal']}  \n"
                        f"Lövések kapura: {s['shots_on_target']}  \n"
                        f"Eredmény: {s['score']}")
    else:
        st.info("Jelenleg nincs jelzés az élő meccsekhez.")

    # Összes élő meccs listája
    st.subheader("Összes élő mérkőzés:")
    for fixture in fixtures:
        league = fixture['league']['name']
        home = fixture['teams']['home']['name']
        away = fixture['teams']['away']['name']
        elapsed = fixture['fixture']['status']['elapsed'] or 0
        score = f"{fixture['goals']['home']} - {fixture['goals']['away']}"
        st.write(f"**{league}**: {home} vs {away} | Eredmény: {score} | Idő: {elapsed} perc")

if __name__ == "__main__":
    main()
