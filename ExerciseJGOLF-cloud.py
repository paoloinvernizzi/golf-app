import streamlit as st
import pandas as pd
import hashlib
import requests
import json
import time

st.set_page_config(page_title="Golf Performance Cloud", layout="wide", page_icon="⛳")

# ==========================================
# FUNZIONI DI SUPPORTO (ISOLATE E COPERTE DA TRY/EXCEPT)
# ==========================================
def invia_dati_cloud(url, dati):
    try:
        inviato = requests.post(
            url, 
            data=json.dumps(dati), 
            headers={"Content-Type": "text/plain"},
            allow_redirects=True
        )
        return inviato.status_code
    except:
        return 500

def ricava_csv_url():
    """Genera l'URL di download CSV in modo sicuro senza rischiare crash di stringa"""
    try:
        if "connections" in st.secrets and "gsheets" in st.secrets["connections"] and "url" in st.secrets["connections"]["gsheets"]:
            base_url = st.secrets["connections"]["gsheets"]["url"]
            if not base_url:
                return None
            if "edit?usp=sharing" in base_url:
                return base_url.replace("edit?usp=sharing", "export?format=csv")
            elif "edit#" in base_url:
                return base_url.split("edit#")[0] + "export?format=csv"
            elif "/export" in base_url:
                return base_url
            else:
                return base_url.rstrip("/") + "/export?format=csv"
    except:
        pass
    return None

def mostra_form_inserimento(esercizi_dict):
    st.markdown("### 🎯 Seleziona la tua sessione")
    
    card1, card2, card3 = st.columns(3)
    with card1:
        st.image("https://unsplash.com", caption="Mobilità e attivazione pre-round", use_container_width=True)
        if st.button("⚡ PRE GARA", use_container_width=True, type="primary" if st.session_state.fase_selezionata == "⚡ Pre Gara" else "secondary"):
            st.session_state.fase_selezionata = "⚡ Pre Gara"
            st.rerun()
            
    with card2:
        st.image("https://unsplash.com", caption="Allungamento e scarico post-round", use_container_width=True)
        if st.button("🧘 POST GARA", use_container_width=True, type="primary" if st.session_state.fase_selezionata == "🧘 Post Gara" else "secondary"):
            st.session_state.fase_selezionata = "🧘 Post Gara"
            st.rerun()
            
    with card3:
        st.image("https://unsplash.com", caption="Potenziamento specifico a casa", use_container_width=True)
        if st.button("🏠 ALLENAMENTO CASA", use_container_width=True, type="primary" if st.session_state.fase_selezionata == "🏠 Allenamento a Casa" else "secondary"):
            st.session_state.fase_selezionata = "🏠 Allenamento a Casa"
            st.rerun()

    st.write("---")
    st.markdown(f"#### 📋 Configura esercizio per: **{st.session_state.fase_selezionata}**")
    
    esercizio_scelto = st.selectbox("Seleziona l'esercizio svolto:", esercizi_dict[st.session_state.fase_selezionata])
    
    col_parametri1, col_parametri2 = st.columns(2)
    with col_parametri1:
        c_serie, c_rep = st.columns(2)
        with c_serie:
            serie = st.number_input("🔢 Serie eseguite:", min_value=1, value=3, key="form_serie")
        with c_rep:
            ripetizioni = st.number_input("🔄 Ripetizioni / Durata (sec):", min_value=1, value=10, key="form_rep")
        
        ha_peso = st.checkbox("Usi pesi / elastici?", value=("Casa" in st.session_state.fase_selezionata), key="form_ha_peso")
        carico = st.number_input("⚖️ Carico (Kg):", min_value=0.0, value=0.0, step=0.5, disabled=not ha_peso, key="form_carico")
        
    with col_parametri2:
        difficolta = st.slider("⭐ Fatica Percepita (Scala RPE 1-5):", min_value=1, max_value=5, value=3, key="form_diff")
        impressioni = st.text_area("💭 Note, dolori o sensazioni della sessione:", key="form_note")

    if st.button("🚀 Sincronizza nel Cloud Team", use_container_width=True):
        try:
            SCRIPT_URL = st.secrets["connections"]["gsheets"].get("script_url", "")
            if not SCRIPT_URL:
                st.error("URL dello Script non configurato nei Secrets.")
            else:
                payload = {
                    "utente": st.session_state.username.strip().lower(),
                    "fase": st.session_state.fase_selezionata,
                    "categoria": "Sessione Diretta",
                    "esercizio": esercizio_scelto,
                    "serie": int(serie),
                    "ripetizioni": int(ripetizioni),
                    "peso": float(carico),
                    "difficolta": int(difficolta),
                    "note": impressioni
                }
                
                status = invia_dati_cloud(SCRIPT_URL, payload)
                if status == 200:
                    st.success("💪 Ottimo lavoro! Sessione salvata sul Cloud. Premi su 'Vedi Progressi' per controllare lo storico.")
                else:
                    st.error(f"Errore di sincronizzazione. Codice: {status}")
        except Exception as e:
            st.error(f"Errore durante l'invio: {e}")

# ==========================================
# 1. CARICAMENTO DATI DA CLOUD (BLINDATO)
# ==========================================
df_completo = pd.DataFrame()
colonne_rilevate = []
link_csv = ricava_csv_url()

if link_csv:
    try:
        live_csv_url = f"{link_csv}&nocache={int(time.time())}"
        df_grezzo = pd.read_csv(live_csv_url)
        if not df_grezzo.empty:
            df_grezzo.columns = df_grezzo.columns.str.strip()
            colonne_rilevate = list(df_grezzo.columns)
            
            # Mappatura posizionale sicura
            mappa = {}
            if len(df_grezzo.columns) >= 2: mappa[df_grezzo.columns[1]] = 'Utente'
            if len(df_grezzo.columns) >= 3: mappa[df_grezzo.columns[2]] = 'Fase'
            if len(df_grezzo.columns) >= 5: mappa[df_grezzo.columns[4]] = 'Esercizio'
            
            for c in df_grezzo.columns:
                if c.lower() in ['difficoltà', 'difficolta', 'diffic']:
                    mappa[c] = 'Difficoltà'
            
            df_completo = df_grezzo.rename(columns=mappa)
    except:
        pass

# ==========================================
# 2. SISTEMA DI CONFIGURAZIONE TEAM
# ==========================================
UTENTI_TEAM = {
    "coach": hashlib.sha256("coachmaster".encode()).hexdigest(),
    "atleta1": hashlib.sha256("golf2026".encode()).hexdigest(),
    "atleta2": hashlib.sha256("golf2026".encode()).hexdigest(),
    "atleta3": hashlib.sha256("golf2026".encode()).hexdigest()
}

DIZIONARIO_ESERCIZI = {
    "⚡ Pre Gara": [
        "🦒 Mobilità collo (Flessione/estensione, Rotazione dx/sx)",
        "🏋️‍♂️ Mobilità spalle con ferro (Sollevare e portare dietro)",
        "🔄 Mobilità dorso (Flessione ginocchia, braccia incrociate)",
        "🏌️‍♂️ Mobilità dorso (Ferro dietro le spalle, rotazione busto)",
        "🎯 Mobilità bacino (Spostamenti laterali, circonduzioni)",
        "🦶 Mobilità piedi/caviglie (Cedimento alternato)",
        "🎗️ Swing con elastico (Solo back - solo finish - completo)",
        "🧎‍♂️ Core: Crunch", "🪲 Core: Dead bug", "🌉 Core: Ponti simmetrici", 
        "🦿 Core: Ponti monolaterali", "⏱️ Core: Plank statico (30-60\")", 
        "🧱 Core: Plank laterale (30-60\")", "🦸‍♂️ Core: Superman", "🏃‍♂️ Core: Mountain climbers"
    ],
    "🧘 Post Gara": [
        "🤚 Stretching M. Estensori Mano (Allungamento dita)",
        "💪 Stretching Avambraccio e Polso (Estensione braccio)",
        "🚪 Stretching Pettorale Monolaterale (Appoggio spalliera)",
        "📐 Stretching M. Dorsale Monolaterale",
        "🏹 Stretching Tricipite Brachiale",
        "🛌 Stretching Piriforme da supino",
        "↔️ Stiramento simmetrico colonna da supino",
        "🐈 Quadrupedia Gobba/Inarcamento Rachide",
        "🧘 Stiramento colonna da seduto sui talloni",
        "⚔️ Stretching Psoas da posizione cavalier servente",
        "🧍 Stretching Tensore Fascia Lata",
        "🪑 Stretching M. Ischio Crurale da seduto"
    ],
    "🏠 Allenamento a Casa": [
        "🏋️‍♂️ Squat con bilanciere o pesi",
        "🔄 Circuito Addome (Crunch+Ponte+Russian Twist+Plank)",
        "🛡️ Affondo anteriore + Rotazione busto con peso",
        "👐 Alzate laterali e frontali monolaterali",
        "🪜 Affondi bulgari con pesi o a corpo libero",
        "🏌️‍♂️ Swing a corpo libero con peso (3 phases)",
        "🏆 Circuito Core Completo (Esercizi da 1 a 8)"
    ]
}

if 'autenticato' not in st.session_state:
    st.session_state.autenticato = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'fase_selezionata' not in st.session_state:
    st.session_state.fase_selezionata = "⚡ Pre Gara"

# ==========================================
# 3. INTERFACCIA UTENTE (SIDEBAR & SCHERMATA LOGIN)
# ==========================================
with st.sidebar:
    st.header("🔐 Accesso Team")
    if not st.session_state.autenticato:
        user_in = st.text_input("Username Atleta:", key="login_user").strip().lower()
        pass_in = st.text_input("Password:", type="password", key="login_pass")
        if st.button("Accedi al Cloud", use_container_width=True):
            hash_in = hashlib.sha256(pass_in.encode()).hexdigest()
            if user_in in UTENTI_TEAM and UTENTI_TEAM[user_in] == hash_in:
                st.session_state.autenticato = True
                st.session_state.username = user_in
                st.rerun()
            else:
                st.error("Credenziali non valide.")
    else:
        st.success(f"🌐 Utente: {st.session_state.username.upper()}")
        if st.button("🚪 Esci", use_container_width=True):
            st.session_state.autenticato = False
            st.session_state.username = ""
            st.rerun()

