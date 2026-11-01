import streamlit as st
import pandas as pd
import hashlib
import requests
import json
import time

st.set_page_config(page_title="Golf Performance Cloud", layout="wide", page_icon="⛳")

# ==========================================
# 1. LETTURA DATI DAL FOGLIO ONLINE (ANTI-CACHE)
# ==========================================
try:
    base_url = st.secrets["connections"]["gsheets"]["url"]
    if "edit?usp=sharing" in base_url:
        csv_url = base_url.replace("edit?usp=sharing", "export?format=csv")
    elif "edit#" in base_url:
        csv_url = base_url.split("edit#")[0] + "export?format=csv"
    else:
        csv_url = base_url + "/export?format=csv"
        
    live_csv_url = f"{csv_url}&nocache={int(time.time())}"
    df_completo = pd.read_csv(live_csv_url)
    df_completo.columns = df_completo.columns.str.strip()
except Exception as e:
    st.error("Configura correttamente il link del tuo Google Sheet nei Secrets della bacheca di Streamlit.")
    st.stop()

# ==========================================
# 2. CREDENZIALI DEL TEAM
# ==========================================
UTENTI_TEAM = {
    "coach": hashlib.sha256("coachmaster".encode()).hexdigest(),
    "atleta1": hashlib.sha256("golf2026".encode()).hexdigest(),
    "atleta2": hashlib.sha256("golf2026".encode()).hexdigest(),
    "atleta3": hashlib.sha256("golf2026".encode()).hexdigest()
}

# ==========================================
# 3. DATABASE ESERCIZI (STRUTTURA AD APP)
# ==========================================
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
# 4. SIDEBAR DI LOG-IN
# ==========================================
with st.sidebar:
    st.header("🔐 Accesso Team")
    if not st.session_state.autenticato:
        user_in = st.text_input("Username Atleta:").strip().lower()
        pass_in = st.text_input("Password:", type="password")
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

# ==========================================
# 5. CONTENUTO PRINCIPALE DELL'APPLICAZIONE
# ==========================================
if not st.session_state.autenticato:
    st.title("⛳ Golf Performance Hub")
    st.info("Accedi con il tuo account in sidebar per visualizzare ed inserire i tuoi dati di allenamento.")
else:
    is_coach = (st.session_state.username == "coach")
    
    col_utente = 'Utente' if 'Utente' in df_completo.columns else ('utente' if 'utente' in df_completo.columns else df_completo.columns[1])
    col_fase = 'Fase' if 'Fase' in df_completo.columns else ('fase' if 'fase' in df_completo.columns else df_completo.columns[2])
    col_diff = 'Difficoltà' if 'Difficoltà' in df_completo.columns else ('difficolta' if 'difficolta' in df_completo.columns else df_completo.columns[-1])

    if is_coach:
        st.title("👨‍🏫 Pannello Coach (Visione Globale)")
        elenco_atleti = ["Tutti"] + [u for u in UTENTI_TEAM.keys() if u != "coach"]
        utente_selezionato = st.selectbox("Seleziona atleta da monitorare:", elenco_atleti)
        if utente_selezionato == "Tutti":
            df_visibile = df_completo
        else:
            df_visibile = df_completo[df_completo[col_utente].astype(str).str.lower().str.strip() == utente_selezionato.lower().strip()]
    else:
        st.title("⛳ Golf Performance Cloud")
        df_visibile = df_completo[df_completo[col_utente].astype(str).str.lower().str.strip() == st.session_state.username.lower().strip()]

    tab_inserimento, tab_dashboard = st.tabs(["📝 Inserisci Allenamento", "📊 Vedi Progressi"])

    # --- TAB INSERIMENTO DATI (INTERFACCIA GRAFICA CARD) ---
    with tab_inserimento:
        if is_coach:
            st.warning("I profili Coach monitorano i dati esclusivamente dalla tab 'Vedi Progressi'. Per registrare esercizi effettua l'accesso come atleta.")
        else:
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
            
            esercizio_scelto = st.selectbox("Seleziona l'esercizio svolto:", DIZIONARIO_ESERCIZI[st.session_state.fase_selezionata])
            
            col_parametri1, col_parametri2 = st.columns(2)
            with col_parametri1:
                c_serie, c_rep = st.columns(2)
                with c_serie:
                    serie = st.number_input("🔢 Serie eseguite:", min_value=1, value=3)
                with c_rep:
                    ripetizioni = st.number_input("🔄 Ripetizioni / Durata (sec):", min_value=1, value=10)
                
                ha_peso = st.checkbox("Usi pesi / elastici?", value=("Casa" in st.session_state.fase_selezionata))
                carico = st.number_input("⚖️ Carico (Kg):", min_value=0.0, value=0.0, step=0.5, disabled=not ha_peso)
                
            with col_parametri2:
                difficolta = st.slider("⭐ Fatica Percepita (Scala RPE 1-5):", min_value=1, max_value=5, value=3)
                impressioni = st.text_area("💭 Note, dolori o sensazioni della sessione:")

            if st.button("🚀 Sincronizza nel Cloud Team", use_container_width=True):
                try:
                    SCRIPT_URL = st.secrets["connections"]["gsheets"].get("script_url", "")
                    if not SCRIPT_URL:
                        st.error("URL dello Script non configurato nei Secrets.")
                    else:
                        # Scrittura forzata del payload su riga singola pulita per evitare SyntaxError
