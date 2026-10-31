import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime 

### Configurazione della pagina

st.set_page_config(page_title="Golf Performance Cloud", layout="wide", page_icon="⛳") 

### Il database ora è un file locale sul server cloud (completamente indipendente e libero)

DB_FILE = "golf_cloud_database.csv" 

### Inizializzazione Database Esercizi se non esiste sul server

if not os.path.exists(DB_FILE):
df_init = pd.DataFrame(columns=[
'Data', 'Utente', 'Fase', 'Gruppo/Tipo', 'Esercizio', 'Serie', 'Ripetizioni', 'Carico (Kg)', 'Difficoltà', 'Impressioni'
])
df_init.to_csv(DB_FILE, index=False) 

def carica_dati():
if os.path.exists(DB_FILE):
return pd.read_csv(DB_FILE)
return pd.DataFrame() 

def salva_dato(nuovo_record):
df = carica_dati()
df = pd.concat([df, pd.DataFrame([nuovo_record])], ignore_index=True)
df.to_csv(DB_FILE, index=False)
return df 

### Database Account del Team (Puoi aggiungere o cambiare i nomi qui)

UTENTI_TEAM = {
"atleta1": hashlib.sha256("golf2026".encode()).hexdigest(),
"atleta2": hashlib.sha256("golf2026".encode()).hexdigest(),
"coach": hashlib.sha256("coachmaster".encode()).hexdigest()
} 

### Dizionario Esercizi con Icone (Protocollo Raduno BG Under 16)

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
"⏱️ 5- Plank (Tenuta 30-60")", "🧱 6- Plank laterale (Tenuta 30-60")",
"🦸‍♂️ 7- Superman", "🏃‍♂️ 8- Mountain climbers (Tenuta 30-60")"
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

### --- BARRA LATERALE ACCESSO ---

with st.sidebar:
st.header("🔐 Accesso Team")
if not st.session_state.autenticato:
user_in = st.text_input("Username Atleta/Coach:").strip().lower()
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
st.success(f"🌐 Cloud Atleta: **{st.session_state.username.upper()}**")
if st.button("🚪 Esci", use_container_width=True):
st.session_state.autenticato = False
st.session_state.username = ""
st.rerun()

### --- CORPO PRINCIPALE ---

if not st.session_state.autenticato:
st.title("⛳ Golf Performance Hub")
st.info("Accedi per sincronizzare i tuoi dati con il Cloud del team.")
else:
is_coach = (st.session_state.username == "coach")
df_completo = carica_dati() 

if is_coach:
st.title("👨‍🏫 Pannello Coach")
utente_selezionato = st.selectbox("Seleziona atleta:", ["Tutti"] + [u for u in UTENTI_TEAM.keys() if u != "coach"])
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
if is_coach:
c3.metric("Atleta più attivo", df_visibile['Utente'].mode().upper() if not df_visibile['Utente'].empty else "N/D")
else:
c3.metric("Fase più eseguita", df_visibile['Fase'].mode() if not df_visibile['Fase'].empty else "N/D")
    st.write("---")
    col_pre, col_post, col_casa = st.columns(3)
    
    with col_pre:
        st.markdown("#### ⚡ PRE GARA")
        sub_pre = df_visibile[df_visibile['Fase'] == "Pre Gara"]
        st.metric("Sessioni", len(sub_pre))
        if not sub_pre.empty: st.bar_chart(sub_pre.set_index('Data')['Difficoltà'], height=130)
            
    with col_post:
        st.markdown("#### 🧘 POST GARA")
        sub_post = df_visibile[df_visibile['Fase'] == "Post Gara"]
        st.metric("Sessioni", len(sub_post))
        if not sub_post.empty: st.bar_chart(sub_post.set_index('Data')['Difficoltà'], height=130)
            
    with col_casa:
        st.markdown("#### 🏠 CASA")
        sub_casa = df_visibile[df_visibile['Fase'] == "Allenamento a Casa"]
        st.metric("Sessioni", len(sub_casa))
        if not sub_casa.empty: st.bar_chart(sub_casa.set_index('Data')['Difficoltà'], height=130)

    st.write("---")
    st.markdown("### 📋 Registro Storico ")
    st.dataframe(df_visibile, use_container_width=True)
