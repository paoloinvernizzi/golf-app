import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime

st.set_page_config(page_title="Golf Performance Cloud", layout="wide", page_icon="⛳")

DB_FILE = "golf_cloud_database.csv"
USERS_FILE = "golf_cloud_users.csv"

if not os.path.exists(DB_FILE):
    df_init = pd.DataFrame(columns=['Data', 'Utente', 'Fase', 'Gruppo/Tipo', 'Esercizio', 'Serie', 'Ripetizioni', 'Carico (Kg)', 'Difficoltà', 'Impressioni'])
    df_init.to_csv(DB_FILE, index=False)

if not os.path.exists(USERS_FILE):
    df_u_init = pd.DataFrame(columns=['Username', 'Password'])
    default_users = [
        {'Username': 'coach', 'Password': hashlib.sha256('coachmaster'.encode()).hexdigest()},
        {'Username': 'atleta1', 'Password': hashlib.sha256('golf2026'.encode()).hexdigest()},
        {'Username': 'atleta2', 'Password': hashlib.sha256('golf2026'.encode()).hexdigest()}
    ]
    df_u_init = pd.concat([df_u_init, pd.DataFrame(default_users)], ignore_index=True)
    df_u_init.to_csv(USERS_FILE, index=False)

def carica_dati():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame()

def salva_dato(nuovo_record):
    df = carica_dati()
    df = pd.concat([df, pd.DataFrame([nuovo_record])], ignore_index=True)
    df.to_csv(DB_FILE, index=False)
    return df

def carica_utenti():
    if os.path.exists(USERS_FILE):
        return pd.read_csv(USERS_FILE)
    return pd.DataFrame(columns=['Username', 'Password'])

def registra_nuovo_utente(username, password):
    df_u = carica_utenti()
    if username in df_u['Username'].values:
        return False
    hashed_p = hashlib.sha256(password.encode()).hexdigest()
    nuovo_u = pd.DataFrame([{'Username': username, 'Password': hashed_p}])
    df_u = pd.concat([df_u, nuovo_u], ignore_index=True)
    df_u.to_csv(USERS_FILE, index=False)
    return True

def verifica_credenziali(username, password):
    df_u = carica_utenti()
    hashed_p = hashlib.sha256(password.encode()).hexdigest()
    return not df_u[(df_u['Username'] == username) & (df_u['Password'] == hashed_p)].empty

DIZIONARIO_ESERCIZI = {
    "⚡ Pre Gara": {
        "🤸‍♂️ Riscaldamento Generale": [
            "🦒 1- Mobilità collo (Flessione/estensione, Rotazione dx/sx)",
            "🏋️‍♂️ 2- Mobilità spalle con ferro (Sollevare e portare dietro)",
            "🔄 3- Mobilità dorso (Flessione ginocchia, braccia incrociate)",
            "🏌️‍♂️ 4- Mobilità dorso (Ferro dietro le spalle, rotazione busto)",
            "🎯 5- Mobilità bacino (Spostamenti laterali, circonduzioni)",
            "🦶 6- Mobilità piedi/caviglie (Cedimento alternato)",
            "🎗️ 7- Swing con elastico (Solo back - solo finish - completo)"
        ],
        "🧘‍♂️ Core Stability (Warmup)": [
            "🧎‍♂️ 1- Crunch", "🪲 2- Dead bug", "🌉 3- Ponti", "🦿 4- Ponti monolaterali",
            "⏱️ 5- Plank (Tenuta 30-60\")", "🧱 6- Plank laterale (Tenuta 30-60\")",
            "🦸‍♂️ 7- Superman", "🏃‍♂️ 8- Mountain climbers (Tenuta 30-60\")"
        ]
    },
    "🧘 Post Gara": {
        "🖐️ Arti Superiori": [
            "🤚 Stretching M. Estensori Mano (Allungamento dita)",
            "💪 Stretching Avambraccio e Polso (Estensione braccio)"
        ],
        "🧣 Braccio e Spalle": [
            "🚪 Stretching Pettorale Monolaterale (Appoggio spalliera)",
            "📐 Stretching M. Dorsale Monolaterale",
            "🏹 Stretching Tricipite Brachiale"
        ],
        "🦴 Rachide / Bacino": [
            "🛌 Stretching Piriforme da supino",
            "↔️ Stiramento simmetrico colonna da supino",
            "🐈 Quadrupedia Gobba/Inarcamento Rachide",
            "🧘 Stiramento colonna da seduto sui talloni"
        ],
        "🦵 Arti Inferiori": [
            "⚔️ Stretching Psoas da posizione cavaliere servente",
            "🧍 Stretching Tensore Fascia Lata",
            "🪑 Stretching M. Ischio Crurale da seduto"
        ]
    },
    "🏠 Allenamento a Casa": {
        "🏋️‍♀️ Preparazione Atletica Specifica": [
            "🏋️‍♂️ Esercizio 1: Squat con bilanciere o pesi",
            "🔄 Esercizio 2: Circuito Addome (Crunch+Ponte+Russian Twist+Plank)",
            "🛡️ Esercizio 3: Affondo anteriore + Rotazione busto con peso",
            "👐 Esercizio 4: Alzate laterali e frontali monolaterali",
            "🪜 Esercizio 5: Affondi bulgari con pesi o a corpo libero",
            "🏌️‍♂️ Esercizio 6: Swing a corpo libero con peso (3 fasi)",
            "🏆 Circuito Core Completo (Esercizi da 1 a 8)"
        ]
    }
}

if 'autenticato' not in st.session_state:
    st.session_state.autenticato = False
if 'username' not in st.session_state:
    st.session_state.username = ""

with st.sidebar:
    st.header("🔐 Accesso Team")
    if not st.session_state.autenticato:
        modalita = st.radio("Scegli un'azione:", ["Accedi al Cloud", "Registra Nuovo Atleta"])
        user_in = st.text_input("Username / Email:").strip().lower()
        pass_in = st.text_input("Password:", type="password")
        if modalita == "Accedi al Cloud":
            if st.button("Entra", use_container_width=True):
                if verifica_credenziali(user_in, pass_in):
                    st.session_state.autenticato = True
                    st.session_state.username = user_in
                    st.rerun()
                else:
                    st.error("Credenziali non valide.")
        else:
            if st.button("Crea Account", use_container_width=True):
                if user_in and pass_in:
                    if registra_nuovo_utente(user_in, pass_in):
                        st.success("✅ Profilo creato! Ora seleziona 'Accedi al Cloud' per entrare.")
                    else:
                        st.error("Questo username è già registrato nel team.")
                else:
                    st.warning("Inserisci sia username che password.")
    else:
        st.success(f"🌐 Cloud Connesso: **{st.session_state.username.upper()}**")
        if st.button("🚪 Esci", use_container_width=True):
            st.session_state.autenticato = False
            st.session_state.username = ""
            st.rerun()

if not st.session_state.autenticato:
    st.title("⛳ Golf Performance Hub")
    st.info("Accedi o crea il tuo account personale dal menu a sinistra per salvare i tuoi allenamenti.")
else:
    is_coach = (st.session_state.username == "coach")
    df_completo = carica_dati()
    if is_coach:
        st.title("👨‍🏫 Pannello Coach (Visione Globale)")
        df_u_registrati = carica_utenti()
        elenco_atleti = ["Tutti"] + [u for u in df_u_registrati['Username'].values if u != "coach"]
        utente_selezionato = st.selectbox("Seleziona atleta:", elenco_atleti)
        df_visibile = df_completo if utente_selezionato == "Tutti" else df_completo[df_completo['Utente'] == utente_selezionato]
    else:
        st.title(f"⛳ Diario di {st.session_state.username.capitalize()}")
        df_visibile = df_completo[df_completo['Utente'] == st.session_state.username]

    tab_inserimento, tab_dashboard = st.tabs(["📝 Inserisci Esercizio", "📊 Vedi Progressi"])

    with tab_inserimento:
        if is_coach:
            st.warning("I coach possono guardare i dati nella tab dei progressi.")
        else:
            st.subheader("📋 Registra esercizio")
            col1, col2 = st.columns(2)
            with col1:
                fase_scelta = st.selectbox("Fase:", list(DIZIONARIO_ESERCIZI.keys()))
                gruppo_scelto = st.selectbox("Categoria:", list(DIZIONARIO_ESERCIZI[fase_scelta].keys()))
                esercizio_scelto = st.selectbox("Esercizio:", DIZIONARIO_ESERCIZI[fase_scelta][gruppo_scelto])
                c_serie, c_rep = st.columns(2)
                with c_serie:
                    serie = st.number_input("🔢 Serie:", min_value=1, value=3)
                with c_rep:
                    ripetizioni = st.number_input("🔄 Ripetizioni / Secondi:", min_value=1, value=10)
            with col2:
                ha_peso = st.checkbox("Usi pesi/sovraccarichi?", value=("Casa" in fase_scelta))
                carico = st.number_input("⚖️ Peso (Kg):", min_value=0.0, value=0.0, step=0.5, disabled=not ha_peso)
                difficolta = st.slider("⭐ Difficoltà Percepita:", min_value=1, max_value=5, value=3)
                impressioni = st.text_area("💭 Note e impressioni:")

            if st.button("🚀 Sincronizza nel Cloud Libero", use_container_width=True):
                orario = datetime.now().strftime("%Y-%m-%d %H:%M")
                nuovo_log = {
                    'Data': orario, 'Utente': st.session_state.username,
                    'Fase': fase_scelta.split(" ", 1)[-1], 'Gruppo/Tipo': gruppo_scelto.split(" ", 1)[-1],
                    'Esercizio': esercizio_scelto.split(" ", 1)[-1], 'Serie': int(serie),
                    'Ripetizioni': int(ripetizioni), 'Carico (Kg)': carico if ha_peso else 0.0,
                    'Difficoltà': difficolta, 'Impressioni': impressioni
                }
                salva_dato(nuovo_log)
                st.success("✅ Salvato nel Cloud di squadra!")
                st.rerun()

    with tab_dashboard:
        st.subheader("📊 Analisi Carichi di Lavoro")
        if df_visibile.empty:
            st.info("Ancora nessun dato registrato su questo account.")
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric("Esercizi Registrati", len(df_visibile))
            c2.metric("Media Fatica", f"{df_visibile['Difficoltà'].mean():.1f} / 5 ⭐")
            
            # Correzione dell'errore sulla stringa .mode()
            if is_coach:
                most_active = df_visibile['Utente'].mode()
                c3.metric("Atleta più attivo", most_active.values[0].upper() if not most_active.empty else "N/D")
            else:
                most_phase = df_visibile['Fase'].mode()
                c3.metric("Fase più eseguita", str(most_phase.values[0]) if not most_phase.empty else "N/D")
