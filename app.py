import streamlit as st
import pandas as pd
import requests
import urllib.parse
from datetime import datetime
import os
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit.components.v1 as components

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(page_title="ATN-Virtual | Crew Center", page_icon="🌺", layout="wide")

# --- GESTION LANGUE (Session) ---
if 'lang' not in st.session_state: st.session_state['lang'] = 'FR'

# --- DICTIONNAIRE DE TRADUCTION ---
TRANS = {
    "FR": {
        "menu_home": "🏠 Accueil",
        "menu_profile": "👤 Mon Espace",
        "menu_briefing": "✈️ Briefing Room",
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
        "leaderboard_title": "🏆 Top 3 - Heures de Vol",
        "recent_flights": "✈️ Vols Récents (Global)",
        "demo_mode": "ℹ️ Mode Démo (Données simulées)",
        "event_title": "Prochains événements",
        "roster_title": "L'Équipe ATN-Virtual",
        "roster_inactive": "⛔ INACTIF",
        "roster_sync": "Données synchronisées avec fsHub",
        "briefing_title": "Préparation du Vol",
        "briefing_desc": "Préparez votre rotation : Météo, Prévisions et Plan de vol.",
        "briefing_dep": "Aéroport de Départ",
        "briefing_arr": "Aéroport d'Arrivée",
        "briefing_ac": "Type d'Appareil",
        "briefing_btn": "Générer le Briefing",
        "briefing_simbrief": "🚀 Ouvrir dans SimBrief",
        "pirep_title": "Soumettre un rapport manuel (PIREP)",
        "pirep_intro": "Formulaire de secours",
        "pirep_warn": "Ce formulaire est réservé aux pilotes rencontrant des difficultés techniques avec le logiciel de suivi (LRM). L'utilisation du client automatique est recommandée pour la précision des données.",
        "pirep_send": "📤 ENVOYER LE RAPPORT (Direct)",
        "contact_title": "Contactez-nous",
        "contact_desc": "Une question ? Une suggestion ? Le Staff est à votre écoute.",
        "contact_send": "📤 ENVOYER LE MESSAGE (Direct)",
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
        "profile_title": "Mon Espace Pilote",
        "profile_career": "Ma Carrière",
        "profile_flights": "Mes Derniers Vols",
        "profile_grade": "Grade Actuel",
        "profile_hours": "Mes Heures",
        "logout": "Déconnexion",
        "ext_tools": "Outils Externes",
        "lang_select": "Langue / Language",
        "email_success": "✅ Message envoyé avec succès au Staff !",
        "email_error": "❌ Erreur lors de l'envoi : "
    },
    "EN": {
        "menu_home": "🏠 Home",
        "menu_profile": "👤 My Profile",
        "menu_briefing": "✈️ Briefing Room",
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
        "leaderboard_title": "🏆 Top 3 - Flight Hours",
        "recent_flights": "✈️ Recent Flights (Global)",
        "demo_mode": "ℹ️ Demo Mode (Simulated Data)",
        "event_title": "Upcoming Events",
        "roster_title": "ATN-Virtual Team",
        "roster_inactive": "⛔ INACTIVE",
        "roster_sync": "Data synced with fsHub",
        "briefing_title": "Flight Preparation",
        "briefing_desc": "Prepare your rotation: Weather, Forecasts, and Flight Plan.",
        "briefing_dep": "Departure Airport",
        "briefing_arr": "Arrival Airport",
        "briefing_ac": "Aircraft Type",
        "briefing_btn": "Generate Briefing",
        "briefing_simbrief": "🚀 Open in SimBrief",
        "pirep_title": "Submit Manual PIREP",
        "pirep_intro": "Backup Form",
        "pirep_warn": "This form is intended for pilots experiencing technical issues with the tracking client (LRM). Please use the automated client whenever possible for data accuracy.",
        "pirep_send": "📤 SUBMIT REPORT (Direct)",
        "contact_title": "Contact Us",
        "contact_desc": "Any questions? Suggestions? The Staff is here to help.",
        "contact_send": "📤 SEND MESSAGE (Direct)",
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
        "profile_title": "My Pilot Area",
        "profile_career": "My Career",
        "profile_flights": "My Last Flights",
        "profile_grade": "Current Rank",
        "profile_hours": "My Hours",
        "logout": "Logout",
        "ext_tools": "External Tools",
        "lang_select": "Langue / Language",
        "email_success": "✅ Message sent successfully!",
        "email_error": "❌ Error sending email: "
    },
    "ES": {
        "menu_home": "🏠 Inicio",
        "menu_profile": "👤 Mi Perfil",
        "menu_briefing": "✈️ Briefing Room",
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
        "leaderboard_title": "🏆 Top 3 - Horas de Vuelo",
        "recent_flights": "✈️ Vuelos Recientes",
        "demo_mode": "ℹ️ Modo Demo (Datos simulados)",
        "event_title": "Próximos Eventos",
        "roster_title": "Equipo ATN-Virtual",
        "roster_inactive": "⛔ INACTIVO",
        "roster_sync": "Datos sincronizados con fsHub",
        "briefing_title": "Preparación de Vuelo",
        "briefing_desc": "Prepara tu rotación: Clima, Pronósticos y Plan de Vuelo.",
        "briefing_dep": "Aeropuerto de Salida",
        "briefing_arr": "Aeropuerto de Llegada",
        "briefing_ac": "Tipo de Avión",
        "briefing_btn": "Generar Briefing",
        "briefing_simbrief": "🚀 Abrir en SimBrief",
        "pirep_title": "Enviar PIREP Manual",
        "pirep_intro": "Formulario de Respaldo",
        "pirep_warn": "Este formulario está reservado para pilotos con problemas técnicos en el cliente (LRM). Se recomienda usar el cliente automático para mayor precisión.",
        "pirep_send": "📤 ENVIAR REPORTE (Directo)",
        "contact_title": "Contáctanos",
        "contact_desc": "¿Necesitas ayuda? Rellena este formulario.",
        "contact_send": "📤 ENVIAR SOLICITUD (Directo)",
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
        "profile_title": "Mi Zona Piloto",
        "profile_career": "Mi Carrera",
        "profile_flights": "Mis Últimos Vuelos",
        "profile_grade": "Rango Actual",
        "profile_hours": "Mis Horas",
        "logout": "Cerrar Sesión",
        "ext_tools": "Herramientas Externas",
        "lang_select": "Langue / Language",
        "email_success": "✅ Mensaje enviado con éxito!",
        "email_error": "❌ Error al enviar: "
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
def get_img_as_base64(file):
    try:
        with open(file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except: return None

LOGO_BASE64 = get_img_as_base64(LOGO_FILE) if os.path.exists(LOGO_FILE) else None
LOGO_URL = f"data:image/png;base64,{LOGO_BASE64}" if LOGO_BASE64 else "https://img.fshub.io/images/airlines/2275/avatar.png"
PILOT_AVATAR_URL = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

st.markdown("""
    <style>
    .big-font { font-size:20px !important; }
    div[data-testid="stMetric"] { background-color: rgb(0, 157, 255) !important; padding: 15px; border-radius: 12px; }
    div[data-testid="stMetric"] label, div[data-testid="stMetricValue"] { color: white !important; }
    div[data-testid="stMetric"] div[data-testid="stMetricDelta"] { color: #e0e0e0 !important; }
    .metar-box { background-color: #e3f2fd; border-left: 5px solid rgb(0, 157, 255); padding: 15px; font-family: monospace; color: black; }
    .stButton button { width: 100%; }
    
    .login-logo-container { display: flex; justify-content: center; width: 100%; margin-bottom: 20px; }
    .login-logo { width: 150px; height: auto; }

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
    {"id": "THT1001", "nom": "Guillaume B.", "grade": "CDB", "role": "STAFF", "fshub_id": "23309", "default": "232h"},
    {"id": "THT1002", "nom": "Alain L.", "grade": "CDB", "role": "STAFF", "fshub_id": "23385", "default": "190h"},
    {"id": "THT1003", "nom": "Andrew F.", "grade": "CDB", "role": "STAFF", "fshub_id": "23387", "default": "598h"},
    {"id": "THT1004", "nom": "Bonno T.", "grade": "PPL", "role": "Pilote", "fshub_id": "23713", "default": "196h"},
    {"id": "THT1005", "nom": "Frédéric B.", "grade": "CPL", "role": "Pilote", "fshub_id": "12054", "default": "288h"},
    {"id": "THT1006", "nom": "Mattias G.", "grade": "CDB", "role": "STAFF", "fshub_id": "28103", "default": "74h"},
    {"id": "THT1007", "nom": "Jordan M.", "grade": "EP", "role": "Pilote", "fshub_id": "19702", "default": "111h"},
    {"id": "THT1008", "nom": "Mathieu G.", "grade": "EP", "role": "Pilote", "fshub_id": "1360", "default": "96h"},
    {"id": "THT1009", "nom": "Daniel V.", "grade": "EP", "role": "Pilote", "fshub_id": "28217", "default": "0h"}, 
    {"id": "THT1010", "nom": "Kévin", "grade": "EP", "role": "Pilote", "fshub_id": "28382", "default": "5h"}
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
    except: return "⚠️ Erreur connexion"

def get_real_taf(icao_code):
    try:
        url = f"https://tgftp.nws.noaa.gov/data/forecasts/taf/stations/{icao_code}.TXT"
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            return response.text
        return "⚠️ TAF indisponible"
    except: return "⚠️ Erreur connexion"

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

# --- ROBOT PUISSANT : SCRAPER LES PILOTES AVEC HEURES ET VOLS ---
@st.cache_data(ttl=3600)
def get_global_pilot_data():
    url = "https://fshub.io/airline/THT/pilots"
    # Dictionnaire : 'NomPilote': {'hours': '123h', 'flights': '45'}
    pilot_data = {}
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        dfs = pd.read_html(url, storage_options=headers)
        if len(dfs) > 0:
            df = dfs[0]
            # On cherche les colonnes intelligemment
            cols_str = [str(c).lower() for c in df.columns]
            
            # Index des colonnes
            try:
                col_pilot_idx = next(i for i, c in enumerate(cols_str) if "pilot" in c)
                col_hrs_idx = next(i for i, c in enumerate(cols_str) if "hour" in c)
                col_flt_idx = next(i for i, c in enumerate(cols_str) if "flight" in c)
                
                for index, row in df.iterrows():
                    p_name = str(row.iloc[col_pilot_idx])
                    p_hours = str(row.iloc[col_hrs_idx])
                    p_flights = str(row.iloc[col_flt_idx])
                    
                    pilot_data[p_name] = {'hours': p_hours, 'flights': p_flights}
            except: pass
    except: return {}
    return pilot_data

@st.cache_data(ttl=300)
def get_fshub_flights():
    url = "https://fshub.io/airline/THT/overview"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        import lxml
        dfs = pd.read_html(url, storage_options=headers)
        for df in dfs:
            if len(df.columns) >= 5: return df, True
        return pd.DataFrame(), False 
    except: return pd.DataFrame(), False

@st.cache_data(ttl=300)
def get_pilot_personal_flights(fshub_id):
    if not fshub_id: return pd.DataFrame(), False
    url = f"https://fshub.io/pilot/{fshub_id}"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        dfs = pd.read_html(url, storage_options=headers)
        for df in dfs:
            cols_str = [str(c).lower() for c in df.columns]
            if len(df.columns) >= 5:
                if any("aircraft" in c for c in cols_str) or any("distance" in c for c in cols_str) or any("time" in c for c in cols_str):
                    return df, True
        return pd.DataFrame(), False
    except: return pd.DataFrame(), False

# --- FONCTION ENVOI EMAIL SMTP ---
def send_email_via_ionos(subject, body):
    try:
        smtp_server = st.secrets["email"]["smtp_server"]
        smtp_port = st.secrets["email"]["smtp_port"]
        username = st.secrets["email"]["username"]
        password = st.secrets["email"]["password"]
        receiver = st.secrets["email"]["receiver_email"]
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = receiver
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
        return True
    except Exception as e:
        return str(e)

# --- 5. SESSION ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'event_participants' not in st.session_state: st.session_state['event_participants'] = {}

# --- 6. LOGIN ---
def login_page():
    st.markdown(f"""<div class="login-logo-container"><img src="{LOGO_URL}" class="login-logo"></div><h1 style='text-align: center;'>CREW CENTER ATN-VIRTUAL VA</h1>""", unsafe_allow_html=True)
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
            st.markdown("""<div style='text-align: center; color: #57606a; margin-bottom: 20px;'>Embarquez pour une expérience immersive au cœur du Pacifique. Du vol inter-îles en ATR au long-courrier en Dreamliner, vivez la simulation autrement dans une ambiance conviviale et professionnelle.</div>""", unsafe_allow_html=True)
            c_invit1, c_invit2 = st.columns(2)
            with c_invit1: st.link_button("📝 Inscription fsHub", "https://fshub.io/airline/THT/overview", use_container_width=True)
            with c_invit2: st.link_button("🌐 Notre Site Web", "https://www.atnvirtual.fr/", use_container_width=True)
            st.markdown("---")
            st.info("ℹ️ **Information d'accès :** Vos identifiants personnels pour ce Crew Center vous seront communiqués par le Staff une fois votre inscription validée sur fsHub.")

if not st.session_state['logged_in']:
    login_page()
else:
    # --- 7. SIDEBAR ---
    with st.sidebar:
        try: st.image(LOGO_URL, width=100)
        except: st.write("🌺 ATN")
        st.title("ATN-Virtual")
        components.html("""<div style="text-align: center; font-family: 'Segoe UI', sans-serif; color: white; background-color: #009dff; padding: 10px; border-radius: 8px;"><div id="date" style="font-size: 14px; margin-bottom: 2px; opacity: 0.9;">--/--/----</div><div id="clock" style="font-size: 22px; font-weight: bold;">--:--:-- Z</div></div><script>function updateTime() {const now = new Date();const time = now.getUTCHours().toString().padStart(2, '0') + ':' + now.getUTCMinutes().toString().padStart(2, '0') + ':' + now.getUTCSeconds().toString().padStart(2, '0') + ' Z';const date = now.getUTCFullYear() + '-' + (now.getUTCMonth() + 1).toString().padStart(2, '0') + '-' + now.getUTCDate().toString().padStart(2, '0');document.getElementById('clock').innerText = time;document.getElementById('date').innerText = date;}setInterval(updateTime, 1000);updateTime();</script>""", height=75)
        st.caption(f"CDB : {st.session_state['username']}")
        if st.button(T("logout")):
            st.session_state['logged_in'] = False
            st.rerun()
        st.markdown("---")
        
        nav_options = [
            T("menu_home"),
            T("menu_profile"),
            T("menu_briefing"),
            T("menu_events"),
            T("menu_roster"),
            T("menu_pirep"),
            T("menu_metar"),
            T("menu_tours"),
            T("menu_checklist"),
            T("menu_contact")
        ]
        selection = st.radio("Navigation", nav_options)
        
        st.markdown("---")
        st.link_button("🌍 Radar Live", "https://fshub.io/airline/THT/radar")
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
        if col_fr.button("🇫🇷 FR"): st.session_