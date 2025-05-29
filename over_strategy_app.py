import streamlit as st
import requests

# Állítsd be az API kulcsod
API_KEY = "iV9xxHhZkgZQqudhrzq2r697fd21b9VcR3z50gSFpXV9K4Yimvj4HWBFf3Mn"
API_URL = "https://api.sportmonks.com/v3/football/livescores"

# Streamlit oldalbeállítások
st.set_page_config(page_title="Élő Sportfogadási Stratégia", layout="wide")
st.title("📊 Élő Sportfogadási Stratégia Jelzések")

st.markdown("🔄 Az adatok valós időben frissülnek az API alapján.")

# API hívás
def get_live_matches():
    try:
        params = {
            "api_token": API_KEY,
            "include": "participants;statistics;scores;time"
        }
        response = requests.get(API_URL, params=params)
        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            st.error(f"Hiba az API elérésében: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Hiba történt: {e}")
        return []

# Meccsek feldolgozása
def analyze_matches(matches):
    goal_70min = []
    first_half_goals = []

    for match in matches:
        try:
            stats = match.get("statistics", [])
            time_info = match.get("time", {})
            scores = match.get("scores", {})
            participants = match.get("participants", [])

            # Kapcsolódó adatok kinyerése
            minute = int(time_info.get("minute", 0))
            home = next((team for team in participants if team["meta"]["location"] == "home"), None)
            away = next((team for team in participants if team["meta"]["location"] == "away"), None)

            home_name = home["name"] if home else "Hazai"
            away_name = away["name"] if away else "Vendég"
            score = f"{scores.get('home_score', 0)} - {scores.get('away_score', 0)}"

            # Lövések és kapura lövések
            home_shots = int(next((s["value"] for s in stats if s["type"] == "shots" and s["participant_id"] == home["id"]), 0))
            away_shots = int(next((s["value"] for s in stats if s["type"] == "shots" and s["participant_id"] == away["id"]), 0))
            home_on_target = int(next((s["value"] for s in stats if s["type"] == "shots_on_target" and s["participant_id"] == home["id"]), 0))
            away_on_target = int(next((s["value"] for s in stats if s["type"] == "shots_on_target" and s["participant_id"] == away["id"]), 0))

            total_shots = home_shots + away_shots
            total_on_target = home_on_target + away_on_target

            # ⏱️ 70. perc utáni gól stratégia
            if minute >= 70 and score in ["0 - 0", "1 - 0", "0 - 1", "1 - 1"] and total_on_target >= 5:
                goal_70min.append(f"{home_name} vs {away_name} | Állás: {score} | Perc: {minute} | Kapura lövések: {total_on_target}")

            # ⏱️ Első félidős gól stratégia
            if 1 <= minute <= 45 and total_shots >= 5 and total_on_target >= 2:
                first_half_goals.append(f"{home_name} vs {away_name} | Perc: {minute} | Lövések: {total_shots} | Kapura: {total_on_target}")

        except Exception as e:
            st.warning(f"Nem sikerült feldolgozni egy meccset: {e}")
            continue

    return goal_70min, first_half_goals

# Lefuttatjuk a stratégiákat
matches = get_live_matches()
goal_70min, first_half_goals = analyze_matches(matches)

# 📢 Eredmények megjelenítése
st.subheader("1️⃣ 70. perc utáni gól stratégia")
if goal_70min:
    for item in goal_70min:
        st.success(item)
else:
    st.info("Nincs olyan meccs, amely megfelel a 70. perc utáni gól stratégiának.")

st.subheader("2️⃣ Első félidő +0.5 gól stratégia")
if first_half_goals:
    for item in first_half_goals:
        st.warning(item)
else:
    st.info("Nincs olyan meccs, amely megfelel az első félidős gól stratégiának.")
