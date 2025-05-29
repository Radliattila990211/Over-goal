import streamlit as st
import requests
from datetime import datetime

API_TOKEN = "iV9xxHhZkgZQqudhrzq2r697fd21b9VcR3z50gSFpXV9K4Yimvj4HWBFf3Mn"
API_URL = f"https://api.sportmonks.com/v3/football/livescores?api_token={API_TOKEN}&include=participants;statistics;scores"

st.set_page_config(page_title="Élő Foci Stratégiák", layout="wide")

st.title("⚽ Élő Foci Fogadási Stratégiák")
st.markdown("""
1️⃣ **70. perc utáni gól stratégia**  
- Élő meccsek  
- Állás: 0-0, 1-0, 1-1, 0-1  
- Gólra utaló statisztikák alapján jelzés (kapuralövések, labdabirtoklás)  
- Bankroll: 5.000 Ft, tét: 500 Ft  

2️⃣ **Első félidő több mint 0,5 gól stratégia**  
- Meccs az első félidőben (1’–45’)  
- Élő statisztikák alapján: legalább 5+ lövés / 2+ kapura  
""")

def fetch_live_matches():
    try:
        resp = requests.get(API_URL, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if "data" not in data or not data["data"]:
            return None, "⚠️ Nem kaptunk vissza meccseket az API-tól."
        return data["data"], None
    except Exception as e:
        return None, f"Hiba az API elérésében: {e}"

def parse_match(match):
    # Csapatok és participant_id-k
    home_team = None
    away_team = None
    home_id = None
    away_id = None
    for p in match.get("participants", []):
        if p.get("meta", {}).get("location") == "home":
            home_team = p.get("name")
            home_id = p.get("id")
        elif p.get("meta", {}).get("location") == "away":
            away_team = p.get("name")
            away_id = p.get("id")

    # Gólok az aktuális állapotban (CURRENT)
    home_goals = 0
    away_goals = 0
    for score in match.get("scores", []):
        if score.get("description") == "CURRENT":
            pid = score.get("participant_id")
            goals = score.get("score", {}).get("goals", 0)
            if pid == home_id:
                home_goals = goals
            elif pid == away_id:
                away_goals = goals

    # Statisztikák (labdabirtoklás, lövések)
    possession_home = 0
    possession_away = 0
    shots_home = 0
    shots_away = 0
    shots_on_target_home = 0
    shots_on_target_away = 0

    for stat in match.get("statistics", []):
        type_id = stat.get("type_id")
        pid = stat.get("participant_id")
        val = stat.get("data", {}).get("value", 0)

        # Labdabirtoklás: type_id = 45
        if type_id == 45:
            if pid == home_id:
                possession_home = val
            elif pid == away_id:
                possession_away = val
        # Lövések száma: type_id = 34
        elif type_id == 34:
            if pid == home_id:
                shots_home = val
            elif pid == away_id:
                shots_away = val
        # Kapura lövések: type_id = 35 (feltételezett, ellenőrizd az API dokumentációt)
        elif type_id == 35:
            if pid == home_id:
                shots_on_target_home = val
            elif pid == away_id:
                shots_on_target_away = val

    # Idő (ha nincs külön time mező, próbáljuk a stage_id vagy description alapján megközelíteni)
    # Nincs direkt perc, ezért nem tudjuk pontosan kinyerni, így a stratégia csak akkor működik, ha a state_id (meccs állapot) vagy egyéb adat alapján szűrünk
    # Itt feltételezünk, hogy a state_id == 3 élő meccs (second half), state_id == 2 első félidő stb.
    # De ha nincs ilyen adat, akkor ezt a szűrést nem tudjuk pontosan megcsinálni

    state_id = match.get("state_id", 0)  # 1: not started, 2: 1st half, 3: 2nd half, 4: ended, stb.

    return {
        "home_team": home_team,
        "away_team": away_team,
        "home_goals": home_goals,
        "away_goals": away_goals,
        "possession_home": possession_home,
        "possession_away": possession_away,
        "shots_home": shots_home,
        "shots_away": shots_away,
        "shots_on_target_home": shots_on_target_home,
        "shots_on_target_away": shots_on_target_away,
        "state_id": state_id,
        "name": match.get("name"),
        "starting_at": match.get("starting_at"),
        "id": match.get("id")
    }

def filter_70_min_goal_strategy(parsed_matches):
    signals = []
    for m in parsed_matches:
        # Csak élő meccsek 2. félidőben (state_id == 3)
        if m["state_id"] != 3:
            continue
        # Állás: 0-0, 1-0, 1-1, 0-1
        goals_tuple = (m["home_goals"], m["away_goals"])
        if goals_tuple not in [(0,0),(1,0),(1,1),(0,1)]:
            continue
        # Jelzés, ha a lövések száma összesen legalább 10 (csak egy példa trigger)
        total_shots = m["shots_home"] + m["shots_away"]
        if total_shots < 10:
            continue
        signals.append(m)
    return signals

def filter_first_half_goal_strategy(parsed_matches):
    signals = []
    for m in parsed_matches:
        # Csak első félidő (state_id == 2)
        if m["state_id"] != 2:
            continue
        # Legalább 1 gól (0,5 gól azaz 1 gól felett)
        total_goals = m["home_goals"] + m["away_goals"]
        if total_goals < 1:
            continue
        # Lövések: legalább 5 lövés összesen
        total_shots = m["shots_home"] + m["shots_away"]
        # Kapura lövések: legalább 2 összesen
        total_shots_on_target = m["shots_on_target_home"] + m["shots_on_target_away"]
        if total_shots >= 5 and total_shots_on_target >= 2:
            signals.append(m)
    return signals


def main():
    matches, error = fetch_live_matches()
    if error:
        st.error(error)
        return
    if not matches:
        st.info("⚠️ Nincs jelenleg élő meccs.")
        return

    parsed_matches = [parse_match(m) for m in matches]

    st.header("1️⃣ 70. perc utáni gól stratégia")
    signals_70 = filter_70_min_goal_strategy(parsed_matches)
    if signals_70:
        for m in signals_70:
            st.markdown(f"**{m['name']}**\n- Állás: {m['home_goals']} - {m['away_goals']}\n- Lövések összesen: {m['shots_home'] + m['shots_away']}")
    else:
        st.info("Nincs olyan meccs, amely megfelel a 70. perc utáni gól stratégiának.")

    st.header("2️⃣ Első félidő +0.5 gól stratégia")
    signals_first_half = filter_first_half_goal_strategy(parsed_matches)
    if signals_first_half:
        for m in signals_first_half:
            st.markdown(f"**{m['name']}**\n- Állás: {m['home_goals']} - {m['away_goals']}\n- Lövések: {m['shots_home'] + m['shots_away']}\n- Kapura lövések: {m['shots_on_target_home'] + m['shots_on_target_away']}")
    else:
        st.info("Nincs olyan meccs, amely megfelel az első félidős gól stratégiának.")

    st.markdown("---")
    st.write(f"Frissítés: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
