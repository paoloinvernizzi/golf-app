import streamlit as st
import pandas as pd
import hashlib, requests, json, time

st.set_page_config(page_title="Golf Performance Cloud", layout="wide", page_icon="⛳")

    try:
        import random
        # Forziamo Google a ignorare la cache lato server con due parametri variabili
        df_utenti = pd.read_csv(f"{csv_url}&sheet=Credenziali&nocache={int(time.time())}&r={random.randint(1,9999)}")
        df_utenti.columns = df_utenti.columns.str.strip()
        
        # Estraiamo correttamente la colonna 0 (Utente) e la colonna 1 (Password) rimuovendo gli spazi vuoti
        col_user = df_utenti.columns[0]
        col_pass = df_utenti.columns[1]
        
        UTENTI_TEAM = dict(zip(
            df_utenti[col_user].astype(str).str.lower().str.strip(), 
            df_utenti[col_pass].astype(str).str.strip()
        ))
    except Exception as errore_lettura:
        # Se c'è un errore reale, lo stampiamo temporaneamente per capire cosa non va
        st.sidebar.warning(f"Lettura online fallita, uso dati locali. Errore: {errore_lettura}")
        UTENTI_TEAM = {"coach": "coachmaster", "atleta1": "golf2026"}

except Exception as e:
    st.error("Configura correttamente il link del tuo Google Sheet nei Secrets.")
    st.stop()

DIZIONARIO_ESERCIZI = {
    "⚡ Pre Gara": ["🦒 Mobilità collo", "🏋️‍♂️ Mobilità spalle con ferro", "🔄 Mobilità dorso ferro", "🎯 Mobilità bacino", "🦶 Mobilità piedi/caviglie", "🎗️ Swing con elastico", "🧎‍♂️ Core: Crunch", "🪲 Core: Dead bug", "🌉 Core: Ponti", "⏱️ Core: Plank"],
    "🧘 Post Gara": ["🤚 Stretching Mani", "💪 Stretching Avambraccio", "🚪 Stretching Pettorale", "📐 Stretching Dorsale", "🏹 Stretching Tricipite", "🛌 Stretching Piriforme", "↔️ Stiramento colonna", "🐈 Quadrupedia Gobba", "🧘 Seduto talloni", "🧍 Stretching Psoas"],
    "🏠 Allenamento a Casa": ["🏋️‍♂️ Squat con pesi", "🔄 Circuito Addome completo", "🛡️ Affondo anteriore + Rotazione", "👐 Alzate laterali", "🪜 Affondi bulgari", "🏌️‍♂️ Swing con peso (3 fasi)", "🏆 Circuito Core Completo"]
}

if 'autenticato' not in st.session_state: st.session_state.autenticato = False
if 'username' not in st.session_state: st.session_state.username = ""
if 'fase_selezionata' not in st.session_state: st.session_state.fase_selezionata = "⚡ Pre Gara"
if 'esercizio_selezionato' not in st.session_state: st.session_state.esercizio_selezionato = ""

lista_esercizi_correnti = DIZIONARIO_ESERCIZI[st.session_state.fase_selezionata]
if st.session_state.esercizio_selezionato not in lista_esercizi_correnti:
    st.session_state.esercizio_selezionato = lista_esercizi_correnti[0]

with st.sidebar:
    st.header("🔐 Accesso Team")
    if not st.session_state.autenticato:
        modalita = st.radio("Cosa vuoi fare?", ["Accedi", "Registrati al Team"])
        user_in = st.text_input("Username Atleta:").strip().lower()
        pass_in = st.text_input("Password:", type="password")
        if modalita == "Accedi":
            if st.button("Accedi al Cloud", use_container_width=True):
                hash_verificare = hashlib.sha256(pass_in.encode()).hexdigest()
                if user_in in UTENTI_TEAM and (UTENTI_TEAM[user_in] == pass_in or UTENTI_TEAM[user_in] == hash_verificare):
                    st.session_state.autenticato, st.session_state.username = True, user_in
                    st.rerun()
                else: 
                    st.error("Credenziali non valide o utente inesistente.")
        else:
            if st.button("Crea Profilo e Registrati", use_container_width=True):
                if len(user_in) < 3 or len(pass_in) < 4:
                    st.error("Scegli un username di almeno 3 caratteri ed una password di almeno 4.")
                elif user_in in UTENTI_TEAM:
                    st.error("Questo username è già stato preso da un altro atleta.")
                else:
                    try:
                        url_script = st.secrets["connections"]["gsheets"]["script_url"]
                        payload_reg = {"azione": "registrazione", "utente": user_in, "password": pass_in}
                        res_reg = requests.post(url_script, data=json.dumps(payload_reg), headers={"Content-Type": "text/plain"}, allow_redirects=True)
                        res_data = res_reg.json() if res_reg.status_code == 200 else {}
                        if res_reg.status_code == 200 and res_data.get("status") != "exists":
                            st.success("🎉 Profilo creato! Seleziona 'Accedi' sopra per entrare.")
                        else:
                            st.error("Impossibile registrarsi: l'utente esiste già online.")
                    except:
                        st.error("Errore di comunicazione durante la registrazione.")
    else:
        st.success(f"🌐 Utente: {st.session_state.username.upper()}")
        if st.button("🚪 Esci", use_container_width=True):
            st.session_state.autenticato, st.session_state.username = False, ""
            st.rerun()

if not st.session_state.autenticato:
    st.title("⛳ Golf Performance Hub")
    st.info("Accedi o registrati nella barra laterale per sincronizzare i tuoi allenamenti.")
else:
    is_coach = (st.session_state.username == "coach")
    col_utente = 'Utente' if 'Utente' in df_completo.columns else ('utente' if 'utente' in df_completo.columns else df_completo.columns[0])
    col_fase = 'Fase' if 'Fase' in df_completo.columns else ('fase' if 'fase' in df_completo.columns else df_completo.columns[1])
    col_diff = 'Difficoltà' if 'Difficoltà' in df_completo.columns else ('difficolta' if 'difficolta' in df_completo.columns else df_completo.columns[-1])

    if is_coach:
        st.title("👨‍🏫 Pannello Coach (Visione Globale)")
        elenco_atleti = ["Tutti"] + list(UTENTI_TEAM.keys())
        sel = st.selectbox("Seleziona atleta:", [a for a in elenco_atleti if a != "coach"])
        df_visibile = df_completo if sel == "Tutti" else df_completo[df_completo[col_utente].astype(str).str.lower().str.strip() == sel.lower().strip()]
    else:
        st.title("⛳ Golf Performance Cloud")
        df_visibile = df_completo[df_completo[col_utente].astype(str).str.lower().str.strip() == st.session_state.username.lower().strip()]

    tab_inserimento, tab_dashboard = st.tabs(["📝 Inserisci Allenamento", "📊 Vedi Progressi"])

    with tab_inserimento:
        if is_coach: 
            st.warning("I profili Coach monitorano i dati esclusivamente dalla tab 'Vedi Progressi'.")
        else:
            st.markdown("### 🎯 1. Seleziona la tua sessione")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown('<div style="background-color: #e8f4f8; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 5px;"><h3>⚡</h3><b>PRE GARA</b></div>', unsafe_allow_html=True)
                if st.button("Attiva Pre Gara", use_container_width=True, type="primary" if st.session_state.fase_selezionata == "⚡ Pre Gara" else "secondary"): 
                    st.session_state.fase_selezionata = "⚡ Pre Gara"
                    st.rerun()
            with c2:
                st.markdown('<div style="background-color: #e8f8f0; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 5px;"><h2>🧘</h2><b>POST GARA</b></div>', unsafe_allow_html=True)
                if st.button("Attiva Post Gara", use_container_width=True, type="primary" if st.session_state.fase_selezionata == "🧘 Post Gara" else "secondary"): 
                    st.session_state.fase_selezionata = "🧘 Post Gara"
                    st.rerun()
            with c3:
                st.markdown('<div style="background-color: #f0f0f0; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 5px;"><h2>🏠</h2><b>A CASA</b></div>', unsafe_allow_html=True)
                if st.button("Attiva Casa", use_container_width=True, type="primary" if st.session_state.fase_selezionata == "🏠 Allenamento a Casa" else "secondary"): 
                    st.session_state.fase_selezionata = "🏠 Allenamento a Casa"
                    st.rerun()

            st.write("---")
            st.markdown(f"### 🏌️‍♂️ 2. Seleziona l'esercizio svolto per **{st.session_state.fase_selezionata}**")
            col_es1, col_es2 = st.columns(2)
            for i, es in enumerate(DIZIONARIO_ESERCIZI[st.session_state.fase_selezionata]):
                target_col = col_es1 if i % 2 == 0 else col_es2
                with target_col:
                    if st.button(es, use_container_width=True, type="primary" if (st.session_state.esercizio_selezionato == es) else "secondary", key=f"btn_es_{i}"):
                        st.session_state.esercizio_selezionato = es
                        st.rerun()
            st.write("---")
            st.markdown(f"### 📋 3. Parametri per: *{st.session_state.esercizio_selezionato}*")
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
                    payload = {"azione": "allenamento", "utente": st.session_state.username, "fase": st.session_state.fase_selezionata, "categoria": "Sessione Diretta", "esercizio": st.session_state.esercizio_selezionato, "serie": int(serie), "ripetizioni": int(ripetizioni), "peso": float(carico), "difficolta": int(difficolta), "note": impressioni}
                    res = requests.post(url_script, data=json.dumps(payload), headers={"Content-Type": "text/plain"}, allow_redirects=True)
                    if res.status_code == 200:
                        st.success("💪 Ottimo lavoro! Sessione salvata nel Cloud.")
                    else:
                        st.error(f"Errore di rete. Codice: {res.status_code}")
                except Exception as err:
                    st.error(f"Impossibile salvare: {err}")

    with tab_dashboard:
        t_col, r_col = st.columns(2)
        with t_col:
            st.subheader("📊 Carichi di Lavoro Live")
        with r_col:
            if st.button("🔄 Aggiorna Dati", use_container_width=True):
                st.rerun()
        
        if df_visibile.empty:
            st.info("Nessun dato registrato al momento nel database Cloud.")
        else:
            k1, k2 = st.columns(2)
            k1.metric("Esercizi Totali", len(df_visibile))
            if col_diff in df_visibile.columns:
                df_visibile[col_diff] = pd.to_numeric(df_visibile[col_diff], errors='coerce')
                k2.metric("Media Fatica Percepita", f"{df_visibile[col_diff].mean():.1f} / 5 ⭐")
            st.write("---")
            st.dataframe(df_visibile, use_container_width=True)
