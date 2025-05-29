import streamlit as st
import requests

# ------------------ BEÁLLÍTÁSOK ------------------

API_TOKEN = "iV9xxHhZkgZQqudhrzq2r697fd21b9VcR3z50gSFpXV9K4Yimvj4HWBFf3Mn"
BASE_URL = "https://api.sportmonks.com/v3/football"
BANKROLL = 5000
TET = 500

# ------------------ SEGÉDFÜGGVÉNYEK ------------------

def get_live_matches():
    url = f"{BASE_URL}/livescores/inplay?api_token={API_TOKEN}&include=participants;statistics;scores;time"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            st.error(f"Hiba az API elérésében: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Hálózati hiba: {e}")
        return []

def parse_teams(match):
    participants = match.get("participants", [])
    home = next((p["name"] for p in participants if p["meta"]["location"] == "home"), "Hazai")
    away = next((p["name"] for p in participants if p["meta"]["location"] == "away"), "Vendég")
    return home, away

def get_stat(match, stat_type, location=None):
    stats = match.get("statistics", [])
    filtered = [s for s in stats if s["type"] == stat_type]
    if location:
        filtered = [s for s in filtered if s.get("location") == location]
    return sum(int(s.get("value", 0)) for s in filtered)

def match_time(match):
    try:
        return int(match.get("time", {}).get("minute", 0))
    except:
        return 0

def get_score(match):
    scores = match.get("scores", {})
    return int(scores.get("home_score", 0)), int(scores.get("away_score", 0))

# ------------------ STRATÉGIÁK ------------------

def strategy_70_min_goal(matches):
    tips = []
    for match in matches:
        try:
            time = match_time(match)
            home_goals, away_goals = get_score(match)
            if time >= 70 and (home_goals, away_goals) in [(0,0), (1,0), (0,1), (1,1)]:
                shots_on_target = get_stat(match, "shots_on_target")
                poss_home = get_stat(match, "possession", "home")
                poss_away = get_stat(match, "possession", "away")
                if shots_on_target >= 6 and (poss_home + poss_away) > 80:
                    home, away = parse_teams(match)
                    tips.append({
                        "match": f"{home} vs {away}",
                        "állás": f"{home_goals}-{away_goals}",
                        "perc": time,
                        "kapuralövések": shots_on_target,
                        "labdabirtoklás": f"{poss_home}% - {poss_away}%"
                    })
        except:
            continue
    return tips

def strategy_first_half_goal(matches):
    tips = []
    for match in matches:
        try:
            time = match_time(match)
            if time <= 45:
                shots = get_stat(match, "shots")
                shots_on_target = get_stat(match, "shots_on_target")
                if shots >= 5 and shots_on_target >= 2:
                    home, away = parse_teams(match)
                    home_goals, away_goals = get_score(match)
                    tips.append({
                        "match": f"{home} vs {away}",
                        "állás": f"{home_goals}-{away_goals}",
                        "perc": time,
                        "lövés összesen": shots,
                        "kapuralövések": shots_on_target
                    })
        except:
            continue
    return tips

# ------------------ STREAMLIT FELÜLET ------------------

st.set_page_config(page_title="⚽ Élő Sportfogadási Stratégia", layout="wide")
st.title("📊 Élő Sportfogadási Stratégia Jelzések")
st.caption("🔄 A meccsek statisztikái valós időben frissülnek a Sportmonks API alapján.")
st.markdown(f"💰 **Bankroll:** {BANKROLL} Ft | 🎯 **Tét meccsenként:** {TET} Ft")

live_matches = get_live_matches()

with st.expander("1️⃣ 70. perc utáni gól stratégia", expanded=True):
    strat1 = strategy_70_min_goal(live_matches)
    if strat1:
        for tip in strat1:
            st.success(f"⚽ {tip['match']} | Állás: {tip['állás']} | {tip['perc']}. perc\n"
                       f"Kapuralövések: {tip['kapuralövések']}, Labdabirtoklás: {tip['labdabirtoklás']}")
    else:
        st.info("Nincs olyan meccs, amely megfelel a 70. perc utáni gól stratégiának.")

with st.expander("2️⃣ Első félidő +0.5 gól stratégia", expanded=True):
    strat2 = strategy_first_half_goal(live_matches)
    if strat2:
        for tip in strat2:
            st.warning(f"📍 {tip['match']} | Állás: {tip['állás']} | {tip['perc']}. perc\n"
                       f"Lövések: {tip['lövés összesen']}, Kapuralövések: {tip['kapuralövések']}")
    else:
        st.info("Nincs olyan meccs, amely megfelel az első félidős gól stratégiának.")
