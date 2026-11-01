import streamlit as st
import pandas as pd
import hashlib, requests, json, time

st.set_page_config(page_title="Golf Performance Cloud", layout="wide", page_icon="⛳")

# ==========================================
# 1. LETTURA DATI DAL FOGLIO ONLINE (ANTI-CACHE)
# ==========================================
try:
    base_url = st.secrets["connections"]["gsheets"]["url"]
    csv_url = base_url.replace("edit?usp=sharing", "export?format=csv") if "edit?usp=sharing" in base_url else (base_url.split("edit#")[0] + "export?format=csv" if "edit#" in base_url else base_url + "/export?format=csv")
    df_completo = pd.read_csv(f"{csv_url}&nocache={int(time.time())}")
    df_completo.columns = df_completo.columns.str.strip()
except Exception as e:
    st.error("Configura correttamente il link del tuo Google Sheet nei Secrets."); st.stop()

UTENTI_TEAM = {
    "coach": hashlib.sha256("coachmaster".encode()).hexdigest(),
    "atleta1": hashlib.sha256("golf2026".encode()).hexdigest(),
    "atleta2": hashlib.sha256("golf2026".encode()).hexdigest(),
    "atleta3": hashlib.sha256("golf2026".encode()).hexdigest()
}

DIZIONARIO_ESERCIZI = {
    "⚡ Pre Gara": ["🦒 Mobilità collo", "🏋️‍♂️ Mobilità spalle con ferro", "🔄 Mobilità dorso ferro", "🎯 Mobilità bacino", "🦶 Mobilità piedi/caviglie", "🎗️ Swing con elastico", "🧎‍♂️ Core: Crunch", "🪲 Core: Dead bug", "🌉 Core: Ponti", "⏱️ Core: Plank"],
    "🧘 Post Gara": ["🤚 Stretching Mani", "💪 Stretching Avambraccio", "🚪 Stretching Pettorale", "📐 Stretching Dorsale", "🏹 Stretching Tricipite", "🛌 Stretching Piriforme", "↔️ Stiramento colonna", "🐈 Quadrupedia Gobba", "🧘 Seduto talloni", "🧍 Stretching Psoas"],
    "🏠 Allenamento a Casa": ["🏋️‍♂️ Squat con pesi", "🔄 Circuito Addome completo", "🛡️ Affondo anteriore + Rotazione", "👐 Alzate laterali", "🪜 Affondi bulgari", "🏌️‍♂️ Swing con peso (3 fasi)", "🏆 Circuito Core Completo"]
}

if 'autenticato' not in st.session_state: st.session_state.autenticato = False
if 'username' not in st.session_state: st.session_state.username = ""
if 'fase_selezionata' not in st.session_state: st.session_state.fase_selezionata = "⚡ Pre Gara"

# ==========================================
# 2. SIDEBAR DI LOG-IN
# ==========================================
with st.sidebar:
    st.header("🔐 Accesso Team")
    if not st.session_state.autenticato:
        user_in = st.text_input("Username Atleta:").strip().lower()
        pass_in = st.text_input("Password:", type="password")
        if st.button("Accedi al Cloud", use_container_width=True):
            if user_in in UTENTI_TEAM and UTENTI_TEAM[user_in] == hashlib.sha256(pass_in.encode()).hexdigest():
                st.session_state.autenticato, st.session_state.username = True, user_in; st.rerun()
            else: st.error("Credenziali non valide.")
    else:
        st.success(f"🌐 Utente: {st.session_state.username.upper()}")
        if st.button("🚪 Esci", use_container_width=True):
            st.session_state.autenticato, st.session_state.username = False, ""; st.rerun()

# ==========================================
# 3. INTERFACCIA PRINCIPALE
# ==========================================
if not st.session_state.autenticato:
    st.title("⛳ Golf Performance Hub")
    st.info("Accedi con il tuo account in sidebar per visualizzare ed inserire i tuoi dati.")
else:
    is_coach = (st.session_state.username == "coach")
    col_utente = 'Utente' if 'Utente' in df_completo.columns else ('utente' if 'utente' in df_completo.columns else df_completo.columns[1])
    col_fase = 'Fase' if 'Fase' in df_completo.columns else ('fase' if 'fase' in df_completo.columns else df_completo.columns[2])
    col_diff = 'Difficoltà' if 'Difficoltà' in df_completo.columns else ('difficolta' if 'difficolta' in df_completo.columns else df_completo.columns[-1])

    if is_coach:
        st.title("👨‍🏫 Pannello Coach (Visione Globale)")
        elenco_atleti = ["Tutti"] + [u for u in UTENTI_TEAM.keys() if u != "coach"]
        sel = st.selectbox("Seleziona atleta:", elenco_atleti)
        df_visibile = df_completo if sel == "Tutti" else df_completo[df_completo[col_utente].astype(str).str.lower().str.strip() == sel.lower().strip()]
    else:
        st.title("⛳ Golf Performance Cloud")
        df_visibile = df_completo[df_completo[col_utente].astype(str).str.lower().str.strip() == st.session_state.username.lower().strip()]

    tab_inserimento, tab_dashboard = st.tabs(["📝 Inserisci Allenamento", "📊 Vedi Progressi"])

    with tab_inserimento:
        if is_coach: st.warning("I profili Coach monitorano i dati esclusivamente dalla tab 'Vedi Progressi'.")
        else:
            st.markdown("### 🎯 Seleziona la tua sessione")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.image("https://unsplash.com", use_container_width=True)
                if st.button("⚡ PRE GARA", use_container_width=True, type="primary" if st.session_state.fase_selezionata == "⚡ Pre Gara" else "secondary"): st.session_state.fase_selezionata = "⚡ Pre Gara"; st.rerun()
            with c2:
                st.image("https://unsplash.com", use_container_width=True)
                if st.button("🧘 POST GARA", use_container_width=True, type="primary" if st.session_state.fase_selezionata == "🧘 Post Gara" else "secondary"): st.session_state.fase_selezionata = "🧘 Post Gara"; st.rerun()
            with c3:
                st.image("https://unsplash.com", use_container_width=True)
                if st.button("🏠 ALLENAMENTO CASA", use_container_width=True, type="primary" if st.session_state.fase_selezionata == "🏠 Allenamento a Casa" else "secondary"): st.session_state.fase_selezionata = "🏠 Allenamento a Casa"; st.rerun()

            st.write("---")
            st.markdown(f"#### 📋 Esercizio per: **{st.session_state.fase_selezionata}**")
            es_scelto = st.selectbox("Seleziona esercizio:", DIZIONARIO_ESERCIZI[st.session_state.fase_selezionata])
            
            cp1, cp2 = st.columns(2)
            with cp1:
                serie = st.number_input("🔢 Serie:", min_value=1, value=3)
                ripetizioni = st.number_input("🔄 Ripetizioni / Sec:", min_value=1, value=10)
                carico = st.number_input("⚖️ Carico (Kg):", min_value=0.0, value=0.0, step=0.5)
            with cp2:
                difficolta = st.slider("⭐ Fatica Percepita (RPE 1-5):", min_value=1, max_value=5, value=3)
                impressioni = st.text_area("💭 Note e sensazioni:")

            if st.button("🚀 Sincronizza nel Cloud Team", use_container_width=True):
                try:
                    url_script = st.secrets["connections"]["gsheets"]["script_url"]
                    payload = {"utente": st.session_state.username, "fase": st.session_state.fase_selezionata, "categoria": "Sessione Diretta", "esercizio": es_scelto, "serie": int(serie), "ripetizioni": int(ripetizioni), "peso": float(carico), "difficolta": int(difficolta), "note": impressioni}
                    res = requests.post(url_script, data=json.dumps(payload), headers={"Content-Type": "text/plain"}, allow_redirects=True)
                    if res.status_code == 200: st.success("💪 Ottimo lavoro! Sessione salvata nel Cloud.")
                    else: st.error(f"Errore di rete. Codice: {res.status_code}")
                except Exception as err: st.error(f"Impossibile salvare: {err}")

    with tab_dashboard:
        t_col, r_col = st.columns(2)
        with t_col: st.subheader("📊 Carichi di Lavoro Live")
        with r_col:
            if st.button("🔄 Aggiorna Dati", use_container_width=True): st.rerun()
        if df_visibile.empty: st.info("Nessun dato registrato al momento nel database Cloud.")
        else:
            k1, k2 = st.columns(2)
            k1.metric("Esercizi Totali", len(df_visibile))
            if col_diff in df_visibile.columns:
                df_visibile[col_diff] = pd.to_numeric(df_visibile[col_diff], errors='coerce')
                k2.metric("Media Fatica Percepita", f"{df_visibile[col_diff].mean():.1f} / 5 ⭐")
            st.write("---")
            st.dataframe(df_visibile, use_container_width=True)
