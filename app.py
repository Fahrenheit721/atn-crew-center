import streamlit as st
import pandas as pd
import requests
import urllib.parse
from datetime import datetime
import os

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(page_title="ATN-Virtual | Crew Center", page_icon="🌺", layout="wide")

# --- GESTION DES IMAGES ---
LOGO_FILE = "u_23309_200.png" 
if os.path.exists(LOGO_FILE):
    LOGO_URL = LOGO_FILE
else:
    LOGO_URL = "https://img.fshub.io/images/airlines/2275/avatar.png"

PILOT_AVATAR_URL = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

st.markdown("""
    <style>
    .big-font { font-size:20px !important; }
    div[data-testid="stMetric"] { background-color: rgb(0, 157, 255) !important; padding: 15px; border-radius: 12px; }
    div[data-testid="stMetric"] label, div[data-testid="stMetricValue"] { color: white !important; }
    div[data-testid="stMetric"] div[data-testid="stMetricDelta"] { color: #e0e0e0 !important; }
    .metar-box { background-color: #e3f2fd; border-left: 5px solid rgb(0, 157, 255); padding: 15px; font-family: monospace; color: black; }
    .stButton button { width: 100%; }
    .pilot-card { background-color: white; border: 1px solid #e0e0e0; border-top: 4px solid rgb(0, 157, 255); border-radius: 12px; padding: 12px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); transition: transform 0.2s; min-height: 140px; display: flex; align-items: center; gap: 15px; }
    .pilot-card:hover { transform: translateY(-3px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
    .pilot-img { width: 64px; height: 64px; border-radius: 50%; border: 3px solid #e3f2fd; object-fit: cover; }
    .pilot-details { flex-grow: 1; }
    .pilot-name { font-size: 16px; font-weight: 700; color: #2c3e50; margin-bottom: 4px; }
    .pilot-rank { background-color: #e3f2fd; color: #007bff; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 700; display: inline-block; margin-bottom: 6px; }
    .pilot-info { font-size: 12px; color: #7f8c8d; margin-top: 2px; display: flex; align-items: center; gap: 5px; }
    .staff-badge { background-color: #c0392b; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 800; margin-left: 5px; text-transform: uppercase; letter-spacing: 0.5px; }
    .flight-card { background-color: white; border-radius: 12px; padding: 16px 24px; margin-bottom: 16px; border-left: 6px solid #009dff; box-shadow: 0 2px 6px rgba(0,0,0,0.06); display: flex; justify-content: space-between; align-items: center; transition: all 0.2s ease; }
    .flight-card:hover { transform: translateX(2px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
    .fc-left { display: flex; flex-direction: column; gap: 4px; }
    .fc-route { font-size: 22px; font-weight: 800; color: #2c3e50; letter-spacing: -0.5px; display: flex; align-items: center; gap: 8px; }
    .fc-arrow { color: #cbd5e1; font-size: 18px; }
    .fc-pilot { font-size: 13px; color: #64748b; font-weight: 600; display: flex; align-items: center; gap: 6px; }
    .fc-right { display: flex; flex-direction: column; align-items: flex-end; gap: 6px; }
    .fc-badges { display: flex; align-items: center; gap: 8px; }
    .badge-aircraft { background-color: #f1f5f9; color: #475569; font-size: 11px; font-weight: 700; padding: 6px 12px; border-radius: 20px; border: 1px solid #e2e8f0; }
    .badge-landing { font-family: 'Courier New', monospace; font-weight: 700; font-size: 12px; padding: 6px 10px; border-radius: 6px; background-color: #f8fafc; border: 1px solid #e2e8f0; }
    .landing-good { color: #16a34a; border-color: #bbf7d0; background-color: #f0fdf4; }
    .landing-hard { color: #dc2626; border-color: #fecaca; background-color: #fef2f2; }
    .fc-date { font-size: 11px; color: #94a3b8; font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SÉCURITÉ HYBRIDE (ANTI-CRASH) ---
try:
    # On essaie de lire le fichier caché
    USERS_DB = st.secrets["users"]
except FileNotFoundError:
    # Si ça rate (erreur rouge), on utilise cette liste de secours TEMPORAIRE
    # Cela permet à l'app de s'ouvrir même si le fichier secrets.toml est mal nommé
    USERS_DB = {
        "admin": "admin",
        "THT23309": "1234",
        "THT23385": "1234"
    }

# --- 3. LISTES ---
LISTE_TOURS = ["Tiare IFR Tour", "World ATN Tour IFR", "Tamure Tour VFR", "Taura'a VFR Tour"]
STAFF_MEMBERS = ["GUILLAUME2", "ANDREW.F", "Alain L", "MattiasG"]

# --- 4. FONCTIONS ---
def get_real_metar(icao_code):
    try:
        url = f"https://tgftp.nws.noaa.gov/data/observations/metar/stations/{icao_code}.TXT"
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            lines = response.text.strip().split('\n')
            return lines[1] if len(lines) >= 2 else response.text
        return "⚠️ Météo indisponible"
    except: return "⚠️ Erreur connexion"

@st.cache_data(ttl=300)
def get_fshub_flights():
    url = "https://fshub.io/airline/THT/overview"
    headers = {'User-Agent': 'Mozilla/5.0'}
    demo_data = pd.DataFrame([
        ["GUILLAUME2", "NTAA", "KLAX", "B789", "08:15", "2024-02-22", "-142 fpm"],
        ["ANDREW.F", "NCRG", "NTAA", "AT76", "00:45", "2024-02-21", "-85 fpm"],
        ["Thepilote987", "NTAA", "NTTB", "DH8D", "00:30", "2024-02-20", "-210 fpm"]
    ], columns=["Pilot", "Dep", "Arr", "Aircraft", "Duration", "Date", "Landing"])
    try:
        import lxml
        dfs = pd.read_html(url, storage_options=headers)
        for df in dfs:
            if len(df.columns) >= 5: return df, True
        return demo_data, False 
    except: return demo_data, False

@st.cache_data(ttl=3600) 
def get_fshub_pilots():
    url = "https://fshub.io/airline/THT/pilots"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        import lxml
        dfs = pd.read_html(url, storage_options=headers)
        if len(dfs) > 0:
            df = dfs[0]
            if len(df.columns) >= 7:
                df.columns.values[0] = 'Pilote'; df.columns.values[1] = 'Grade'
                df.columns.values[4] = 'Statut'; df.columns.values[5] = 'Dernière Activité'
                df.columns.values[6] = 'Membre Depuis'
                return df, True
        return None, False
    except: return None, False

# --- 5. SESSION ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'event_participants' not in st.session_state: st.session_state['event_participants'] = {}

# --- 6. LOGIN ---
def login_page():
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        try: st.image(LOGO_URL, width=150)
        except: pass
    st.markdown("<h1 style='text-align: center;'>Crew Center</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login"):
            u = st.text_input("Identifiant")
            p = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Se connecter ✈️"):
                # VERIFICATION SECURISEE VIA ST.SECRETS
                if u in USERS_DB and USERS_DB[u] == p:
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = u
                    st.rerun()
                else: st.error("❌ Erreur connexion")
        st.write("")
        st.markdown("---")
        with st.container(border=True):
            st.markdown("### 🌟 Rejoignez l'aventure !")
            c_invit1, c_invit2 = st.columns(2)
            with c_invit1: st.link_button("📝 Inscription fsHub", "https://fshub.io/airline/THT/overview", use_container_width=True)
            with c_invit2: st.link_button("🌐 Notre Site Web", "https://www.atnvirtual.fr/", use_container_width=True)

if not st.session_state['logged_in']:
    login_page()
else:
    # --- 7. SIDEBAR ---
    with st.sidebar:
        try: st.image(LOGO_URL, width=100)
        except: st.write("🌺 ATN")
        st.title("ATN-Virtual")
        st.caption(f"CDB : {st.session_state['username']}")
        if st.button("Déconnexion"):
            st.session_state['logged_in'] = False
            st.rerun()
        st.markdown("---")
        menu = st.radio("Navigation", ["Accueil", "📅 Événements", "Roster Pilotes", "🏆 Validation Tours"])
        st.markdown("---")
        st.link_button("🌍 WebEye", "https://webeye.ivao.aero")
        st.link_button("📊 fsHub", "https://fshub.io/airline/THT/overview")

    # --- CONTENU ---
    if menu == "Accueil":
        st.title("🌺 Ia Ora Na E Maeva sur le Crew Center ATN-VIRTUAL")
        st.markdown(f"<div class='metar-box'>{get_real_metar('NTAA')}</div>", unsafe_allow_html=True)
        st.write("")
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Pilotes", "19", "Actifs"); c2.metric("Heures", "1,254 h", "+12h")
        c3.metric("Vols", "342", "fsHub"); c4.metric("Landing", "-182 fpm", "Moyen")
        st.markdown("---")
        st.subheader("✈️ Vols Récents")
        flights_df, success = get_fshub_flights()
        display_flights = flights_df.head(5)
        for index, row in display_flights.iterrows():
            try:
                pilot = row.iloc[0]; dep = row.iloc[1]; arr = row.iloc[2]; aircraft = row.iloc[3]
                landing_val = str(row.iloc[6]) if len(row) > 6 else "-"
                landing_cls = "landing-good"
                if "fpm" in landing_val:
                    try:
                        if int(landing_val.replace("fpm","").replace("-","").strip()) > 400: landing_cls = "landing-hard"
                    except: pass
                date_txt = row.iloc[5] if len(row) > 5 else "Aujourd'hui"
                st.markdown(f"""
                <div class="flight-card">
                    <div class="fc-left"><div class="fc-route">{dep} <span class="fc-arrow">➝</span> {arr}</div><div class="fc-pilot">👨‍✈️ {pilot}</div></div>
                    <div class="fc-right"><div class="fc-badges"><span class="badge-aircraft">✈️ {aircraft}</span><span class="badge-landing {landing_cls}">📉 {landing_val}</span></div><div class="fc-date">{date_txt}</div></div>
                </div>""", unsafe_allow_html=True)
            except: continue
        if not success: st.caption("ℹ️ Mode Démo (Données simulées)")

    elif menu == "📅 Événements":
        st.title("📅 Calendrier")
        st.info("🎉 1 An de la VA | 22 Fév - 19h00 Z | Hub NTAA")
        c1,c2,c3 = st.columns(3)
        uid = st.session_state['username']
        if c1.button("✅ Présent"): st.session_state['event_participants'][uid] = "Présent"
        if c2.button("🤔 Peut-être"): st.session_state['event_participants'][uid] = "Incertain"
        if c3.button("❌ Absent"): st.session_state['event_participants'][uid] = "Absent"
        if st.session_state['event_participants']: st.dataframe(pd.DataFrame(list(st.session_state['event_participants'].items()), columns=['Pilote', 'Statut']), use_container_width=True)

    elif menu == "Roster Pilotes":
        st.title("👨‍✈️ L'Équipe ATN-Virtual")
        st.write("Liste officielle des pilotes, synchronisée avec fsHub.")
        st.markdown("---")
        df_pilots, success = get_fshub_pilots()
        if success and df_pilots is not None:
            nb_pilots = len(df_pilots)
            cols_per_row = 3
            for i in range(0, nb_pilots, cols_per_row):
                cols = st.columns(cols_per_row)
                for j in range(cols_per_row):
                    if i + j < nb_pilots:
                        pilot = df_pilots.iloc[i + j]
                        staff_badge = ""
                        if str(pilot['Pilote']).strip() in STAFF_MEMBERS: staff_badge = '<span class="staff-badge">STAFF</span>'
                        with cols[j]:
                            st.markdown(f"""
                            <div class="pilot-card">
                                <img src="{PILOT_AVATAR_URL}" class="pilot-img">
                                <div class="pilot-details">
                                    <div class="pilot-name">{pilot['Pilote']} {staff_badge}</div>
                                    <div class="pilot-rank">{pilot['Grade']}</div>
                                    <div class="pilot-info">📡 {pilot['Statut']}</div>
                                    <div class="pilot-info">👁️ {pilot['Dernière Activité']}</div>
                                </div>
                            </div>""", unsafe_allow_html=True)
        else: st.warning("Impossible de récupérer la liste des pilotes.")

    elif menu == "🏆 Validation Tours":
        st.title("🏆 Validation d'Étape de Tour")
        st.info("Utilisez ce formulaire uniquement pour valider une étape de tour pilote.")
        with st.container(border=True):
            col_main1, col_main2 = st.columns(2)
            with col_main1:
                st.write("### 📍 Informations Tour")
                selected_tour = st.selectbox("Sélectionner le Tour concerné", LISTE_TOURS)
                leg_number = st.number_input("Numéro de l'étape", min_value=1, max_value=12, value=1, step=1)
                st.write("### ✈️ Informations Vol")
                callsign = st.text_input("Callsign", value=st.session_state['username'], disabled=True)
                aircraft = st.text_input("Appareil utilisé", placeholder="ex: B789")
            with col_main2:
                st.write("### 🕰️ Horaires (ZULU)")
                c1, c2 = st.columns(2)
                dep_icao = c1.text_input("Départ (ICAO)", max_chars=4).upper()
                arr_icao = c2.text_input("Arrivée (ICAO)", max_chars=4).upper()
                date_flight = st.date_input("Date du vol")
                flight_time = st.text_input("Temps de vol (Block)", placeholder="ex: 01:45")
            comment = st.text_area("Lien du rapport fsHub (Optionnel) ou Remarques")
            subject = f"VALIDATION TOUR - {selected_tour} - Etape {leg_number} - {st.session_state['username']}"
            email_body = f"PILOTE: {st.session_state['username']}\nTOUR: {selected_tour}\nETAPE: {leg_number}\nREMARQUES: {comment}"
            link = f"mailto:besnier.guillaume@yahoo.fr?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(email_body)}"
            st.markdown("---")
            st.markdown(f"""<a href="{link}" target="_blank"><button style="width:100%; background-color:#009dff; color:white; padding:15px; border-radius:10px; border:none; font-weight:bold; cursor:pointer;">✅ ENVOYER LA VALIDATION</button></a>""", unsafe_allow_html=True)