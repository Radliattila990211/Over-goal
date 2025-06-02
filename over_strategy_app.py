import streamlit as st
import requests
import datetime

# Sportmonks API beállítás
API_TOKEN = "iV9xxHhZkgZQqudhrzq2r697fd21b9VcR3z50gSFpXV9K4Yimvj4HWBFf3Mn"
BASE_URL = "https://api.sportmonks.com/v3/football"

headers = {
    "Authorization": f"Bearer {API_TOKEN}"
}

st.set_page_config(page_title="⚽ Élő Foci Fogadási Stratégia", layout="wide")

st.title("⚽ Élő Foci Fogadási Stratégia")

# --- FÜLEK: Élő stratégia | BTTS stratégia ---
tabs = st.tabs(["🎯 Élő stratégia – 1. félidő +0.5 gól", "📊 BTTS meccs előtti ajánlások"])

# -----------------------------
# 1️⃣ Élő stratégia fül
# -----------------------------
with tabs[0]:
    st.header("🎯 Élő meccsek: 1. félidő +0.5 gól stratégia")

    # Élő meccsek lekérése
    url = f"{BASE_URL}/livescores?include=participants,scores"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json().get("data", [])

        # Szűrés: 1. félidőben 0-0 állás + 15. perc után
        signals = []
        for match in data:
            try:
                home = match["participants"][0]["name"]
                away = match["participants"][1]["name"]
                score = match["scores"]
                minute = int(match["time"]["minute"])
                status = match["time"]["status"]

                home_goals = int(score["home_score"])
                away_goals = int(score["away_score"])

                if (
                    status == "1st Half"
                    and home_goals == 0 and away_goals == 0
                    and minute >= 15
                ):
                    signals.append({
                        "Hazai": home,
                        "Vendég": away,
                        "Perc": minute,
                        "Állás": f"{home_goals}-{away_goals}"
                    })

            except Exception as e:
                continue

        if signals:
            st.success(f"📡 {len(signals)} mérkőzés megfelel a stratégiának!")
            st.dataframe(signals, use_container_width=True)
        else:
            st.warning("❌ Jelenleg nincs olyan élő mérkőzés, amely megfelelne a stratégiának.")
    else:
        st.error("❌ Hiba történt az API elérésében.")

# -----------------------------
# 2️⃣ BTTS stratégia fül
# -----------------------------
with tabs[1]:
    st.header("📊 Meccs előtti BTTS stratégia (Mindkét csapat szerez gólt)")

    # Napi mérkőzések lekérése
    today = datetime.date.today().isoformat()
    url = f"{BASE_URL}/fixtures/date/{today}?include=participants"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        matches = response.json().get("data", [])
        btts_candidates = []

        for match in matches:
            try:
                teams = match["participants"]
                home_team = teams[0]["name"]
                away_team = teams[1]["name"]

                # (Feltétel: mindkét csapat gólátlaga >= 2.5) – itt csak fiktív logika, mivel nincs gólátlag API
                # Feltételezzük, hogy név alapján kiszűrjük a „top” támadó csapatokat (demó logika)
                attacking_keywords = ["Ajax", "PSG", "Barcelona", "Bayern", "Liverpool", "Real", "Man", "Arsenal", "Dortmund", "Leverkusen"]

                if any(team in home_team for team in attacking_keywords) and any(team in away_team for team in attacking_keywords):
                    btts_candidates.append({
                        "Hazai csapat": home_team,
                        "Vendég csapat": away_team
                    })

            except Exception:
                continue

        if btts_candidates:
            st.success(f"📌 {len(btts_candidates)} BTTS tipp érhető el mára.")
            st.dataframe(btts_candidates, use_container_width=True)
        else:
            st.info("💤 Ma nincs olyan meccs, amely megfelelne a BTTS kritériumnak.")
    else:
        st.error("❌ Hiba történt az API elérésében.")
