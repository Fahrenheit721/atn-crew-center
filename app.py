import streamlit as st
import pandas as pd
import requests
import urllib.parse
from datetime import datetime
import os
import streamlit.components.v1 as components

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(page_title="ATN-Virtual | Crew Center", page_icon="🌺", layout="wide")

# --- GESTION LANGUE (Session) ---
if 'lang' not in st.session_state: st.session_state['lang'] = 'FR'

# --- DICTIONNAIRE DE TRADUCTION ---
TRANS = {
    "FR": {
        "menu_home": "🏠 Accueil",
        "menu_events": "📅 Événements",
        "menu_roster": "👨‍✈️ Roster Pilotes",
        "menu_radar": "🌍 Radar Live",
        "menu_pirep": "📝 PIREP Manuel",
        "menu_metar": "🌦️ Météo / METAR",
        "menu_tours": "🏆 Validation Tours",
        "menu_checklist": "📋 Checklist (BETA)",
        "menu_contact": "📞 Contact",
        
        "title_home": "Ia Ora Na",
        "stats_pilots": "Pilotes Actifs",
        "stats_hours": "Heures Totales",
        "stats_flights": "Vols Effectués",
        "stats_landing": "Landing Moyen",
        "recent_flights": "✈️ Vols Récents",
        "demo_mode": "ℹ️ Mode Démo (Données simulées)",
        
        "event_title": "Prochains événements",
        
        "roster_title": "L'Équipe ATN-Virtual",
        "roster_inactive": "⛔ INACTIF",
        "roster_sync": "Synchronisation fsHub...",
        
        "radar_title": "Suivi des Vols en Direct",
        "radar_desc": "Pour des raisons de sécurité imposées par fsHub, la carte ne peut pas s'afficher directement ici. Cliquez ci-dessous pour ouvrir le radar plein écran.",
        "radar_btn": "🌍 OUVRIR LE RADAR LIVE (Nouvel Onglet)",
        
        "pirep_title": "Soumettre un rapport manuel (PIREP)",
        "pirep_intro": "Formulaire de secours",
        "pirep_warn": "Ce formulaire est réservé aux pilotes rencontrant des difficultés techniques avec le logiciel de suivi (LRM). L'utilisation du client automatique est recommandée pour la précision des données.",
        "pirep_send": "📤 SOUMETTRE LE RAPPORT",
        
        "contact_title": "Contactez-nous",
        "contact_desc": "Une question ? Une suggestion ? Le Staff est à votre écoute.",
        "contact_send": "📤 PRÉPARER MON EMAIL",
        "form_subject": "Sujet de votre message",
        "form_msg": "Votre message détaillé...",
        "form_dep": "🛫 Départ (OACI)",
        "form_arr": "🛬 Arrivée (OACI)",
        "form_aircraft": "✈️ Type Appareil",
        "form_flight_nb": "🔢 Numéro de Vol",
        "form_landing": "📉 Taux Atterrissage",
        "form_time_dep": "🕒 Heure Départ (UTC)",
        "form_time_arr": "🕒 Heure Arrivée (UTC)",
        "form_date_dep": "📅 Date de Départ",
        "form_date_arr": "📅 Date d'Arrivée",
        
        "metar_title": "Météo Aéronautique",
        "metar_desc": "Bulletin en temps réel & Décodage rapide.",
        "metar_label": "Rechercher un aéroport (Code OACI)",
        "metar_btn": "🔍 Analyser Météo",
        "metar_raw": "Bulletin Brut (Source NOAA)",
        "metar_decoded": "Données Clés",
        
        "checklist_title": "Checklist Airbus A320 Family",
        "checklist_info": "⚠️ MODULE EN DÉVELOPPEMENT : Cette checklist interactive est actuellement en phase de test (BETA). Elle est conçue pour la famille A320 (A319/A320/A321) et sera amenée à évoluer prochainement avec de nouvelles fonctionnalités.",
        "checklist_complete": "✅ CHECKLIST COMPLETED",
        "checklist_reset": "🔄 Réinitialiser la Checklist",
        
        "logout": "Déconnexion",
        "ext_tools": "Outils Externes",
        "lang_select": "Langue / Language"
    },
    "EN": {
        "menu_home": "🏠 Home",
        "menu_events": "📅 Events",
        "menu_roster": "👨‍✈️ Pilot Roster",
        "menu_radar": "🌍 Live Radar",
        "menu_pirep": "📝 Manual PIREP",
        "menu_metar": "🌦️ Weather / METAR",
        "menu_tours": "🏆 Tour Validation",
        "menu_checklist": "📋 Checklist (BETA)",
        "menu_contact": "📞 Contact",
        
        "title_home": "Ia Ora Na",
        "stats_pilots": "Active Pilots",
        "stats_hours": "Total Hours",
        "stats_flights": "Flights Flown",
        "stats_landing": "Avg Landing",
        "recent_flights": "✈️ Recent Flights",
        "demo_mode": "ℹ️ Demo Mode (Simulated Data)",
        "event_title": "Upcoming Events",
        "roster_title": "ATN-Virtual Team",
        "roster_inactive": "⛔ INACTIVE",
        "roster_sync": "Syncing fsHub...",
        "radar_title": "Live Flight Tracking",
        "radar_desc": "Due to security restrictions from fsHub, the map cannot be displayed directly here. Click below to open the full-screen radar.",
        "radar_btn": "🌍 OPEN LIVE RADAR (New Tab)",
        "pirep_title": "Submit Manual PIREP",
        "pirep_intro": "Backup Form",
        "pirep_warn": "This form is intended for pilots experiencing technical issues with the tracking client (LRM). Please use the automated client whenever possible for data accuracy.",
        "pirep_send": "📤 SUBMIT REPORT",
        "contact_title": "Contact Us",
        "contact_desc": "Any questions? Suggestions? The Staff is here to help.",
        "contact_send": "📤 PREPARE EMAIL",
        "form_subject": "Subject",
        "form_msg": "Your detailed message...",
        "form_dep": "🛫 Departure (ICAO)",
        "form_arr": "🛬 Arrival (ICAO)",
        "form_aircraft": "✈️ Aircraft Type",
        "form_flight_nb": "🔢 Flight Number",
        "form_landing": "📉 Landing Rate",
        "form_time_dep": "🕒 Dep Time (UTC)",
        "form_time_arr": "🕒 Arr Time (UTC)",
        "form_date_dep": "📅 Departure Date",
        "form_date_arr": "📅 Arrival Date",
        "metar_title": "Aviation Weather",
        "metar_desc": "Real-time bulletin & Quick decode.",
        "metar_label": "Search Airport (ICAO Code)",
        "metar_btn": "🔍 Analyze Weather",
        "metar_raw": "Raw Bulletin (NOAA Source)",
        "metar_decoded": "Key Data",
        "checklist_title": "Airbus A320 Family Checklist",
        "checklist_info": "⚠️ UNDER DEVELOPMENT: This interactive checklist is currently in BETA testing phase. It is designed for the A320 Family (A319/A320/A321) and will evolve soon with new features.",
        "checklist_complete": "✅ CHECKLIST COMPLETED",
        "checklist_reset": "🔄 Reset Checklist",
        "logout": "Logout",
        "ext_tools": "External Tools",
        "lang_select": "Langue / Language"
    },
    "ES": {
        "menu_home": "🏠 Inicio",
        "menu_events": "📅 Eventos",
        "menu_roster": "👨‍✈️ Lista de Pilotos",
        "menu_radar": "🌍 Radar en Vivo",
        "menu_pirep": "📝 PIREP Manual",
        "menu_metar": "🌦️ Clima / METAR",
        "menu_tours": "🏆 Validación Tours",
        "menu_checklist": "📋 Checklist (BETA)",
        "menu_contact": "📞 Contacto",
        
        "title_home": "Ia Ora Na",
        "stats_pilots": "Pilotos Activos",
        "stats_hours": "Horas Totales",
        "stats_flights": "Vuelos Realizados",
        "stats_landing": "Aterrizaje Prom.",
        "recent_flights": "✈️ Vuelos Recientes",
        "demo_mode": "ℹ️ Modo Demo (Datos simulados)",
        "event_title": "Próximos Eventos",
        "roster_title": "Equipo ATN-Virtual",
        "roster_inactive": "⛔ INACTIVO",
        "roster_sync": "Sincronizando fsHub...",
        "radar_title": "Rastreo de Vuelos en Vivo",
        "radar_desc": "Debido a restricciones de seguridad de fsHub, el mapa no se puede mostrar aquí. Haga clic abajo para abrir el radar.",
        "radar_btn": "🌍 ABRIR RADAR EN VIVO (Nueva Pestaña)",
        "pirep_title": "Enviar PIREP Manual",
        "pirep_intro": "Formulario de Respaldo",
        "pirep_warn": "Este formulario está reservado para pilotos con problemas técnicos en el cliente (LRM). Se recomienda usar el cliente automático para mayor precisión.",
        "pirep_send": "📤 ENVIAR REPORTE",
        "contact_title": "Contáctanos",
        "contact_desc": "¿Necesitas ayuda? Rellena este formulario.",
        "contact_send": "📤 ENVIAR SOLICITUD",
        "form_subject": "Asunto",
        "form_msg": "Mensaje",
        "form_dep": "🛫 Salida (OACI)",
        "form_arr": "🛬 Llegada (OACI)",
        "form_aircraft": "✈️ Tipo Avión",
        "form_flight_nb": "🔢 Número Vuelo",
        "form_landing": "📉 Tasa Aterrizaje",
        "form_time_dep": "🕒 Hora Salida (UTC)",
        "form_time_arr": "🕒 Hora Llegada (UTC)",
        "form_date_dep": "📅 Fecha Salida",
        "form_date_arr": "📅 Fecha Llegada",
        "metar_title": "Clima Aeronáutico",
        "metar_desc": "Boletín en tiempo real y decodificación rápida.",
        "metar_label": "Buscar Aeropuerto (Código OACI)",
        "metar_btn": "🔍 Analizar Clima",
        "metar_raw": "Boletín Bruto (Fuente NOAA)",
        "metar_decoded": "Datos Clave",
        "checklist_title": "Checklist Normal A320",
        "checklist_info": "⚠️ EN DESARROLLO: Esta checklist interactiva está en fase BETA. Diseñada para la familia A320 (A319/A320/A321) y evolucionará pronto.",
        "checklist_complete": "✅ CHECKLIST COMPLETED",
        "checklist_reset": "🔄 Reiniciar Checklist",
        "logout": "Cerrar Sesión",
        "ext_tools": "Herramientas Externas",
        "lang_select": "Langue / Language"
    }
}

def T(key): return TRANS[st.session_state['lang']][key]

# --- DONNEES CHECKLIST ---
A320_CHECKLIST_DATA = {
    "BEFORE START": ["Cockpit Prep ... COMPLETED", "Gear Pins ... REMOVED", "Signs ... ON/AUTO", "ADIRS ... NAV", "Fuel ... QTY CHECK", "Baro Ref ... SET", "Windows/Doors ... CLOSED", "Beacon ... ON", "Thr Levers ... IDLE", "Parking Brake ... SET"],
    "AFTER START": ["Anti Ice ... AS RQRD", "ECAM Status ... CHECKED", "Pitch Trim ... SET", "Rudder Trim ... ZERO"],
    "BEFORE TAKEOFF": ["Flt Controls ... CHECKED", "Flt Inst ... CHECKED", "Briefing ... CONFIRMED", "Flaps ... SET", "V1/VR/V2 ... SET", "ATC ... SET", "ECAM Memo ... TO NO BLUE"],
    "AFTER TAKEOFF": ["Ldg Gear ... UP", "Flaps ... RETRACTED", "Packs ... ON", "Baro Ref ... STD"],
    "APPROACH": ["Briefing ... CONFIRMED", "ECAM Status ... CHECKED", "Seat Belts ... ON", "Baro Ref ... SET", "MDA/DH ... SET", "Eng Mode ... AS RQRD"],
    "LANDING": ["Cabin Crew ... ADVISED", "A/Thr ... SPEED/OFF", "Auto Brake ... AS RQRD", "ECAM Memo ... LDG NO BLUE"],
    "AFTER LANDING": ["Flaps ... RETRACTED", "Spoilers ... DISARMED", "APU ... START", "Radar ... OFF"],
    "PARKING": ["APU Bleed ... ON", "Engines ... OFF", "Seat Belts ... OFF", "Ext Lt ... OFF", "Fuel Pumps ... OFF", "Park Brk ... SET"],
    "SECURING": ["ADIRS ... OFF", "Oxygen ... OFF", "APU Bleed ... OFF", "Emer Exit Lt ... OFF", "Bat ... OFF"]
}

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
    div[data-testid="stImage"] { display: flex; justify-content: center; }

    /* STYLE ROSTER */
    .pilot-card { background-color: white; border: 1px solid #e0e0e0; border-top: 4px solid rgb(0, 157, 255); border-radius: 12px; padding: 12px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); transition: transform 0.2s; min-height: 140px; display: flex; align-items: center; gap: 15px; }
    .pilot-card:hover { transform: translateY(-3px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
    .pilot-img { width: 64px; height: 64px; border-radius: 50%; border: 3px solid #e3f2fd; object-fit: cover; }
    .pilot-details { flex-grow: 1; }
    .pilot-name { font-size: 18px; font-weight: 800; color: #2c3e50; margin-bottom: 4px; }
    .rank-line { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
    .pilot-rank { background-color: #e3f2fd; color: #007bff; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 700; }
    .staff-badge { background-color: #d32f2f; color: white; padding: 3px 8px; border-radius: 12px; font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; }
    .pilot-info { font-size: 12px; color: #7f8c8d; margin-top: 2px; display: flex; align-items: center; gap: 5px; }
    
    /* BADGE INACTIF */
    .badge-inactive { background-color: #95a5a6; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 11px; }

    /* STYLE FLIGHT CARD */
    .flight-card { background-color: white; border-radius: 12px; padding: 16px 24px; margin-bottom: 16px; border-left: 6px solid #009dff; box-shadow: 0 2px 6px rgba(0,0,0,0.06); display: flex; justify-content: space-between; align-items: center; transition: all 0.2s ease; }
    .flight-card:hover { transform: translateX(2px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
    .fc-left { display: flex; flex-direction: column; gap: 4px; }
    .fc-route { font-size: 22px; font-weight: 800; color: #2c3e50; letter-spacing: -0.5px; display: flex; align-items: center; gap: 8px; }
    .fc-pilot { font-size: 13px; color: #64748b; font-weight: 600; display: flex; align-items: center; gap: 6px; }
    .fc-right { display: flex; flex-direction: column; align-items: flex-end; gap: 6px; }
    .fc-badges { display: flex; align-items: center; gap: 8px; }
    .badge-aircraft { background-color: #f1f5f9; color: #475569; font-size: 11px; font-weight: 700; padding: 6px 12px; border-radius: 20px; border: 1px solid #e2e8f0; }
    .badge-landing { font-family: 'Courier New', monospace; font-weight: 700; font-size: 12px; padding: 6px 10px; border-radius: 6px; background-color: #f8fafc; border: 1px solid #e2e8f0; }
    .landing-good { color: #16a34a; border-color: #bbf7d0; background-color: #f0fdf4; }
    .landing-hard { color: #dc2626; border-color: #fecaca; background-color: #fef2f2; }
    .fc-date { font-size: 11px; color: #94a3b8; font-weight: 500; }
    
    /* STYLE EVENT CARD */
    .event-card { background-color: white; border-radius: 12px; padding: 0; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); display: flex; overflow: hidden; border: 1px solid #f1f5f9; }
    .ev-date-box { background-color: #009dff; color: white; width: 80px; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 15px; }
    .ev-day { font-size: 24px; font-weight: 800; line-height: 1; }
    .ev-month { font-size: 12px; font-weight: 700; text-transform: uppercase; margin-top: 4px; }
    .ev-details { padding: 15px 20px; flex-grow: 1; display: flex; flex-direction: column; justify-content: center; }
    .ev-title { font-size: 18px; font-weight: 800; color: #2c3e50; margin-bottom: 6px; }
    .ev-meta { font-size: 13px; color: #64748b; display: flex; gap: 15px; align-items: center; }
    .ev-tag { background: #f1f5f9; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 11px; color: #475569; }

    .center-text { text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SÉCURITÉ ---
try:
    USERS_DB = st.secrets["users"]
except FileNotFoundError:
    USERS_DB = { "admin": "admin", "THT1001": "1234" }

# --- 3. DONNÉES ROSTER ---
ROSTER_DATA = [
    {"id": "THT1001", "nom": "Guillaume B.", "grade": "CDB", "role": "STAFF", "fshub_id": "23309"},
    {"id": "THT1002", "nom": "Alain L.", "grade": "CDB", "role": "STAFF", "fshub_id": "23385"},
    {"id": "THT1003", "nom": "Andrew F.", "grade": "CDB", "role": "STAFF", "fshub_id": "23387"},
    {"id": "THT1004", "nom": "Bertrand G.", "grade": "OPL", "role": "Pilote", "fshub_id": ""},
    {"id": "THT1005", "nom": "Jean-Pierre V.", "grade": "CDB", "role": "Pilote", "fshub_id": "22712"},
    {"id": "THT1006", "nom": "Isaac H.", "grade": "OPL", "role": "Pilote", "fshub_id": ""},
    {"id": "THT1007", "nom": "Bonno T.", "grade": "CDB", "role": "Pilote", "fshub_id": "23713"},
    {"id": "THT1008", "nom": "Raiarii F.", "grade": "OPL", "role": "Pilote", "fshub_id": ""},
    {"id": "THT1009", "nom": "Frédéric B.", "grade": "CDB", "role": "Pilote", "fshub_id": "12054"},
    {"id": "THT1010", "nom": "Adolphe T.", "grade": "OPL", "role": "Pilote", "fshub_id": ""},
    {"id": "THT1011", "nom": "Natea R.", "grade": "OPL", "role": "Pilote", "fshub_id": "24319"},
    {"id": "THT1012", "nom": "Toanui P.", "grade": "OPL", "role": "Pilote", "fshub_id": ""},
    {"id": "THT1013", "nom": "KEANU F.", "grade": "OPL", "role": "Pilote", "fshub_id": ""},
    {"id": "THT1014", "nom": "LISANDRU S.", "grade": "OPL", "role": "Pilote", "fshub_id": ""},
    {"id": "THT1015", "nom": "Ryron P.", "grade": "OPL", "role": "Pilote", "fshub_id": ""},
    {"id": "THT1016", "nom": "Pascal C.", "grade": "OPL", "role": "Pilote", "fshub_id": ""},
    {"id": "THT1017", "nom": "Angelo D.", "grade": "OPL", "role": "Pilote", "fshub_id": ""},
    {"id": "THT1018", "nom": "Jordan M.", "grade": "OPL", "role": "Pilote", "fshub_id": "19702"},
    {"id": "THT1019", "nom": "MATHIEU G.", "grade": "OPL", "role": "Pilote", "fshub_id": "1360"},
    {"id": "THT1020", "nom": "Matthias G.", "grade": "CDB", "role": "STAFF", "fshub_id": "28103"},
    {"id": "THT1021", "nom": "DANIEL V.", "grade": "OPL", "role": "Pilote", "fshub_id": ""}
]
LISTE_TOURS = ["Tiare IFR Tour", "World ATN Tour IFR", "Tamure Tour VFR", "Taura'a VFR Tour"]

# --- 4. FONCTIONS ---
def get_real_metar(icao_code):
    try:
        url = f"https://tgftp.nws.noaa.gov/data/observations/metar/stations/{icao_code}.TXT"
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            lines = response.text.strip().split('\n')
            return lines[1] if len(lines) >= 2 else response.text
        return "⚠️ Météo indisponible / METAR unavailable"
    except: return "⚠️ Erreur connexion / Connection error"

def extract_metar_data(raw_text):
    data = {"Wind": "N/A", "Temp": "N/A", "QNH": "N/A"}
    try:
        parts = raw_text.split()
        for part in parts:
            if part.endswith("KT"): data["Wind"] = part
            elif "/" in part and len(part) < 7: data["Temp"] = part
            elif part.startswith("Q") and len(part) == 5: data["QNH"] = part
            elif part.startswith("A") and len(part) == 5 and part[1:].isdigit(): data["QNH"] = part
    except: pass
    return data

@st.cache_data(ttl=3600)
def get_pilot_live_hours(fshub_id):
    if not fshub_id: return None
    url = f"https://fshub.io/pilot/{fshub_id}"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        dfs = pd.read_html(url, storage_options=headers)
        for df in dfs:
            df.columns = df.columns.str.strip()
            if 'Airline' in df.columns:
                row = df[df['Airline'].astype(str).str.contains("THT|ATN", case=False, na=False)]
                if not row.empty:
                    for col in df.columns:
                        if "Hour" in col or "Time" in col: return row.iloc[0][col]
    except: return None
    return None

@st.cache_data(ttl=300)
def get_fshub_flights():
    url = "https://fshub.io/airline/THT/overview"
    headers = {'User-Agent': 'Mozilla/5.0'}
    demo_data = pd.DataFrame([
        ["THT1001", "NTAA", "KLAX", "B789", "08:15", "2024-02-22", "-142 fpm"],
        ["THT1003", "NCRG", "NTAA", "AT76", "00:45", "2024-02-21", "-85 fpm"],
        ["THT1009", "NTAA", "NTTB", "DH8D", "00:30", "2024-02-20", "-210 fpm"]
    ], columns=["Pilot", "Dep", "Arr", "Aircraft", "Duration", "Date", "Landing"])
    try:
        import lxml
        dfs = pd.read_html(url, storage_options=headers)
        for df in dfs:
            if len(df.columns) >= 5: return df, True
        return demo_data, False 
    except: return demo_data, False

# --- 5. SESSION ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'event_participants' not in st.session_state: st.session_state['event_participants'] = {}

# --- 6. LOGIN ---
def login_page():
    c1, c2, c3 = st.columns([1, 1, 1]) 
    with c2:
        try: st.image(LOGO_URL, width=150)
        except: pass
    
    st.markdown("<h1 style='text-align: center;'>CREW CENTER ATN-VIRTUAL VA</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login"):
            u = st.text_input("Identifiant")
            p = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Se connecter ✈️"):
                if u in USERS_DB and USERS_DB[u] == p:
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = u
                    st.rerun()
                else: st.error("❌ Erreur connexion")
        st.write("")
        st.markdown("---")
        with st.container(border=True):
            st.markdown("<h3 class='center-text'>🌟 Rejoignez l'aventure !</h3>", unsafe_allow_html=True)
            # --- MODIFICATION TEXTE MARKETING ---
            st.markdown("""
            <div style='text-align: center; color: #57606a; margin-bottom: 20px;'>
            Embarquez pour une expérience immersive au cœur du Pacifique. 
            Du vol inter-îles en ATR au long-courrier en Dreamliner, 
            vivez la simulation autrement dans une ambiance conviviale et professionnelle.
            </div>
            """, unsafe_allow_html=True)
            # ------------------------------------
            c_invit1, c_invit2 = st.columns(2)
            with c_invit1: st.link_button("📝 Inscription fsHub", "https://fshub.io/airline/THT/overview", use_container_width=True)
            with c_invit2: st.link_button("🌐 Notre Site Web", "https://www.atnvirtual.fr/", use_container_width=True)
            
            st.markdown("---")
            # --- MODIFICATION INFO ACCES ---
            st.info("ℹ️ **Information d'accès :** Vos identifiants personnels pour ce Crew Center vous seront communiqués par le Staff une fois votre inscription validée sur fsHub.")
            # -------------------------------

if not st.session_state['logged_in']:
    login_page()
else:
    # --- 7. SIDEBAR ---
    with st.sidebar:
        try: st.image(LOGO_URL, width=100)
        except: st.write("🌺 ATN")
        
        st.title("ATN-Virtual")
        
        # --- HORLOGE ZULU & DATE ---
        components.html(
            """
            <div style="text-align: center; font-family: 'Segoe UI', sans-serif; color: white; background-color: #009dff; padding: 10px; border-radius: 8px;">
                <div id="date" style="font-size: 14px; margin-bottom: 2px; opacity: 0.9;">--/--/----</div>
                <div id="clock" style="font-size: 22px; font-weight: bold;">--:--:-- Z</div>
            </div>
            <script>
            function updateTime() {
                const now = new Date();
                const time = now.getUTCHours().toString().padStart(2, '0') + ':' +
                             now.getUTCMinutes().toString().padStart(2, '0') + ':' +
                             now.getUTCSeconds().toString().padStart(2, '0') + ' Z';
                const date = now.getUTCFullYear() + '-' +
                             (now.getUTCMonth() + 1).toString().padStart(2, '0') + '-' +
                             now.getUTCDate().toString().padStart(2, '0');
                             
                document.getElementById('clock').innerText = time;
                document.getElementById('date').innerText = date;
            }
            setInterval(updateTime, 1000);
            updateTime();
            </script>
            """,
            height=75
        )
        
        st.caption(f"CDB : {st.session_state['username']}")
        if st.button(T("logout")):
            st.session_state['logged_in'] = False
            st.rerun()
        st.markdown("---")
        
        nav_options = [
            T("menu_home"),
            T("menu_events"),
            T("menu_roster"),
            T("menu_radar"),
            T("menu_pirep"),
            T("menu_metar"),
            T("menu_tours"),
            T("menu_checklist"),
            T("menu_contact")
        ]
        
        selection = st.radio("Navigation", nav_options)
        
        st.markdown("---")
        st.link_button("💬 Discord", "https://discord.gg/BQqtsrFJ")
        st.link_button("🌐 Site Officiel", "https://www.atnvirtual.fr/")
        st.caption(T("ext_tools"))
        col_s1, col_s2 = st.columns(2)
        with col_s1: st.link_button("🌍 WebEye", "https://webeye.ivao.aero")
        with col_s2: st.link_button("📊 fsHub", "https://fshub.io/airline/THT/overview")

        st.markdown("---")
        st.caption(T("lang_select"))
        col_fr, col_en, col_es = st.columns(3)
        if col_fr.button("🇫🇷 FR"): st.session_state['lang'] = 'FR'
        if col_en.button("🇬🇧 EN"): st.session_state['lang'] = 'EN'
        if col_es.button("🇪🇸 ES"): st.session_state['lang'] = 'ES'

    # --- CONTENU ---
    
    # ACCUEIL
    if selection == T("menu_home"):
        st.title(f"🌺 {T('title_home')} {st.session_state['username']}")
        metar_ntaa = get_real_metar('NTAA')
        data_ntaa = extract_metar_data(metar_ntaa)
        with st.expander(f"🌦️ Météo Tahiti (NTAA)", expanded=False):
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("Vent", data_ntaa["Wind"])
            mc2.metric("Temp", data_ntaa["Temp"])
            mc3.metric("QNH", data_ntaa["QNH"])
            st.caption(metar_ntaa)
        st.write("")
        c1,c2,c3,c4 = st.columns(4)
        c1.metric(T("stats_pilots"), str(len(ROSTER_DATA)), "Actifs")
        c2.metric(T("stats_hours"), "1,254 h", "+12h")
        c3.metric(T("stats_flights"), "342", "▲")
        c4.metric(T("stats_landing"), "-182 fpm", "Moyen")
        st.markdown("---")
        st.subheader(T("recent_flights"))
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
                    <div class="fc-left"><div class="fc-route">{dep} - {arr}</div><div class="fc-pilot">👨‍✈️ {pilot}</div></div>
                    <div class="fc-right"><div class="fc-badges"><span class="badge-aircraft">✈️ {aircraft}</span><span class="badge-landing {landing_cls}">📉 {landing_val}</span></div><div class="fc-date">{date_txt}</div></div>
                </div>""", unsafe_allow_html=True)
            except: continue
        if not success: st.caption(T("demo_mode"))

    # EVENEMENTS
    elif selection == T("menu_events"):
        st.title(T("event_title"))
        st.markdown("""
        <div class="event-card">
            <div class="ev-date-box"><div class="ev-day">22</div><div class="ev-month">FÉV</div></div>
            <div class="ev-details">
                <div class="ev-title">🎉 1 An de la VA</div>
                <div class="ev-meta"><span>🕒 19:00 Z</span><span>📍 Hub NTAA</span><span class="ev-tag">Event Hub</span></div>
            </div>
        </div>""", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns([1, 1, 1, 3])
        uid = st.session_state['username']
        with c1:
            if st.button("✅ Présent", key="evt1_yes"): st.session_state['event_participants'][uid] = "Présent"
        with c2:
            if st.button("🤔 Peut-être", key="evt1_maybe"): st.session_state['event_participants'][uid] = "Incertain"
        with c3:
            if st.button("❌ Absent", key="evt1_no"): st.session_state['event_participants'][uid] = "Absent"
        st.markdown("---")
        if st.session_state['event_participants']: 
            st.write("### 👥 Participants")
            st.dataframe(pd.DataFrame(list(st.session_state['event_participants'].items()), columns=['Pilote', 'Statut']), use_container_width=True)

    # ROSTER (LIVE HOURS)
    elif selection == T("menu_roster"):
        st.title(T("roster_title"))
        st.caption(T("roster_sync"))
        st.markdown("---")
        
        cols_per_row = 3
        for i in range(0, len(ROSTER_DATA), cols_per_row):
            cols = st.columns(cols_per_row)
            for j in range(cols_per_row):
                if i + j < len(ROSTER_DATA):
                    pilot = ROSTER_DATA[i + j]
                    staff_html = ""
                    if pilot['role'] == "STAFF": staff_html = '<span class="staff-badge">STAFF</span>'
                    
                    live_hours = get_pilot_live_hours(pilot['fshub_id'])
                    
                    if live_hours:
                        heures_display = f"⏱️ {live_hours}"
                    else:
                        heures_display = f"<span class='badge-inactive'>{T('roster_inactive')}</span>"
                    
                    with cols[j]:
                        st.markdown(f"""<div class="pilot-card"><img src="{PILOT_AVATAR_URL}" class="pilot-img"><div class="pilot-details"><div class="pilot-name">{pilot['id']} - {pilot['nom']}</div><div class="rank-line"><span class="pilot-rank">{pilot['grade']}</span>{staff_html}</div><div class="pilot-info">{heures_display}</div></div></div>""", unsafe_allow_html=True)

    # CHECKLIST A320
    elif selection == T("menu_checklist"):
        st.title(T("checklist_title"))
        st.warning(T("checklist_info"))
        
        if st.button(T("checklist_reset")):
            for key in st.session_state.keys():
                if key.startswith("chk_"): st.session_state[key] = False
            st.rerun()
        
        for phase, items in A320_CHECKLIST_DATA.items():
            with st.expander(f"🔹 {phase}", expanded=False):
                completed = True
                for i, item in enumerate(items):
                    key = f"chk_{phase}_{i}"
                    if not st.checkbox(item, key=key): completed = False
                if completed:
                    st.success(T("checklist_complete"))
                    st.balloons()

    # RADAR LIVE
    elif selection == T("menu_radar"):
        st.title(T("radar_title"))
        st.info(T("radar_desc"))
        st.link_button(T("radar_btn"), "https://fshub.io/airline/THT/radar")

    # PIREP
    elif selection == T("menu_pirep"):
        st.title(T("pirep_title"))
        with st.expander(T("pirep_intro"), expanded=True):
            st.info(T("pirep_warn"))
            c_fp_1, c_fp_2, c_fp_rate = st.columns([2, 2, 1])
            p_flight_nb = c_fp_1.text_input(T("form_flight_nb"), placeholder="ex: TN08")
            p_aircraft = c_fp_2.selectbox(T("form_aircraft"), ["B789", "A359", "A320", "AT76", "DH8D", "B350", "C172"])
            p_landing = c_fp_rate.number_input(T("form_landing"), value=-200, step=10)
            c_fp_3, c_fp_4 = st.columns(2)
            p_dep = c_fp_3.text_input(T("form_dep"), max_chars=4, placeholder="NTAA").upper()
            p_arr = c_fp_4.text_input(T("form_arr"), max_chars=4, placeholder="KLAX").upper()
            st.markdown("---")
            c_fp_5, c_fp_6 = st.columns(2)
            p_date_dep = c_fp_5.date_input(T("form_date_dep"))
            p_time_dep = c_fp_6.text_input(T("form_time_dep"), placeholder="HH:MM")
            c_fp_7, c_fp_8 = st.columns(2)
            p_date_arr = c_fp_7.date_input(T("form_date_arr"))
            p_time_arr = c_fp_8.text_input(T("form_time_arr"), placeholder="HH:MM")
            st.markdown("---")
            p_remark = st.text_area(T("form_msg") + " (Optionnel)")
            if st.button(T("pirep_send"), type="primary"):
                if p_flight_nb and p_dep and p_arr:
                    subject_email = f"[PIREP] {p_flight_nb} : {p_dep}-{p_arr}"
                    body_email = f"""
                    PILOTE: {st.session_state['username']}
                    VOL: {p_flight_nb}
                    AVION: {p_aircraft}
                    DEPART: {p_dep} le {p_date_dep} à {p_time_dep}z
                    ARRIVEE: {p_arr} le {p_date_arr} à {p_time_arr}z
                    LANDING: {p_landing} fpm
                    REMARQUES: {p_remark}
                    """
                    link_pirep = f"mailto:contact@atnvirtual.fr?subject={urllib.parse.quote(subject_email)}&body={urllib.parse.quote(body_email)}"
                    st.markdown(f'<meta http-equiv="refresh" content="0;url={link_pirep}">', unsafe_allow_html=True)
                    st.success("✅ Rapport prêt ! Vérifiez votre logiciel de messagerie.")
                else:
                    st.error("⚠️ Veuillez remplir au moins le N° de Vol, Départ et Arrivée.")

    # METAR ON DEMAND
    elif selection == T("menu_metar"):
        st.title(T("metar_title"))
        st.write(T("metar_desc"))
        with st.container(border=True):
            c_met_1, c_met_2 = st.columns([3, 1])
            with c_met_1: icao_search = st.text_input(T("metar_label"), max_chars=4, placeholder="ex: NTAA").upper()
            with c_met_2:
                st.write(""); st.write("")
                search_btn = st.button(T("metar_btn"), type="primary", use_container_width=True)
            if search_btn and icao_search:
                st.markdown("---")
                raw_metar = get_real_metar(icao_search)
                if "⚠️" not in raw_metar:
                    data = extract_metar_data(raw_metar)
                    st.subheader(f"📍 {icao_search} - {T('metar_decoded')}")
                    m1, m2, m3 = st.columns(3)
                    m1.metric("💨 Vent / Wind", data["Wind"])
                    m2.metric("🌡️ Temp.", data["Temp"])
                    m3.metric("⏱️ QNH", data["QNH"])
                    st.write("")
                    st.caption(T("metar_raw"))
                    st.code(raw_metar, language="text")
                else: st.error(raw_metar)

    # VALIDATION TOURS
    elif selection == T("menu_tours"):
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
    
    # CONTACT
    elif selection == T("menu_contact"):
        st.title(T("contact_title"))
        
        c_contact_1, c_contact_2 = st.columns([1, 2])
        
        with c_contact_1:
            try: st.image(LOGO_URL, width=150)
            except: pass
            st.write("### ATN-Virtual Staff")
            st.info(T("contact_desc"))
            st.caption("Réponse sous 24/48h")
        
        with c_contact_2:
            with st.container(border=True):
                st.write("#### 📩 Formulaire")
                st.text_input("De (Expéditeur)", value=st.session_state['username'], disabled=True)
                sujet_contact = st.text_input(T("form_subject"), placeholder="ex: Problème PIREP...")
                message_contact = st.text_area(T("form_msg"), height=150)
                
                subject_email = f"[Crew Center] {sujet_contact}" if sujet_contact else "[Crew Center] Nouvelle demande"
                body_email = f"De: {st.session_state['username']}\n\n{message_contact}" if message_contact else f"De: {st.session_state['username']}\n\n..."
                link_contact = f"mailto:contact@atnvirtual.fr?subject={urllib.parse.quote(subject_email)}&body={urllib.parse.quote(body_email)}"
                
                st.markdown(f"""
                <a href="{link_contact}" target="_blank" style="text-decoration:none;">
                    <button style="width:100%; background-color:#009dff; color:white; padding:15px; border-radius:8px; border:none; font-weight:bold; cursor:pointer; font-size:16px; margin-top:10px;">
                        {T("contact_send")} ✈️
                    </button>
                </a>
                """, unsafe_allow_html=True)