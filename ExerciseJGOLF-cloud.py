import streamlit as st
import pandas as pd
import hashlib, requests, json, time, random

st.set_page_config(page_title="Golf Performance Cloud", layout="wide", page_icon="⛳")

# ---------- STILE ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=Inter:wght@400;500;600&display=swap');
:root{--verde:#14532d;--verde2:#16a34a;--sabbia:#f6f3ea;--oro:#c9a227;--testo:#1f2937;}
html, body, [class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background:linear-gradient(180deg,#f6f3ea 0%,#eef5ee 100%);}
h1,h2,h3{font-family:'Playfair Display',serif !important;color:var(--verde);}
.hero{background:linear-gradient(135deg,#14532d 0%,#16a34a 100%);color:#fff;padding:28px 32px;
      border-radius:20px;margin-bottom:22px;box-shadow:0 10px 30px rgba(20,83,45,.25);}
.hero h1{color:#fff !important;margin:0;font-size:2.1rem;}
.hero p{margin:6px 0 0;opacity:.9;}
.fase{padding:18px;border-radius:16px;text-align:center;margin-bottom:8px;
      box-shadow:0 4px 14px rgba(0,0,0,.06);border:2px solid transparent;transition:.2s;}
.fase .ico{font-size:2rem;}
.fase b{letter-spacing:.08em;color:var(--verde);}
.fase.attiva{border-color:var(--oro);transform:translateY(-2px);box-shadow:0 8px 20px rgba(201,162,39,.35);}
.step{display:inline-block;background:var(--verde);color:#fff;width:30px;height:30px;line-height:30px;
      text-align:center;border-radius:50%;margin-right:10px;font-weight:700;}
.stButton>button{border-radius:12px;font-weight:600;border:1px solid #d6e4d6;padding:.55rem 1rem;}
.stButton>button[kind="primary"]{background:var(--verde2);border-color:var(--verde2);color:#fff;}
.stButton>button:hover{border-color:var(--verde2);color:var(--verde);}
.stButton>button[kind="primary"]:hover{color:#fff;filter:brightness(1.08);}
[data-testid="stMetric"]{background:#fff;padding:18px 20px;border-radius:16px;
      box-shadow:0 4px 14px rgba(0,0,0,.06);border-left:6px solid var(--oro);}
[data-testid="stSidebar"]{background:#14532d;}
[data-testid="stSidebar"] *{color:#f6f3ea !important;}
[data-testid="stSidebar"] input{color:#1f2937 !important;}
.stTabs [data-baseweb="tab"]{font-weight:600;font-size:1rem;}
.stTabs [aria-selected="true"]{color:var(--verde) !important;}
</style>
""", unsafe_allow_html=True)

def hero(titolo, sotto):
    st.markdown(f'<div class="hero"><h1>{titolo}</h1><p>{sotto}</p></div>', unsafe_allow_html=True)

def step(n, testo):
    st.markdown(f'<h3><span class="step">{n}</span>{testo}</h3>', unsafe_allow_html=True)

if 'nuovo_utente_locale' not in st.session_state:
    st.session_state.nuovo_utente_locale = {}

# Utenti fissi di emergenza locali
UTENTI_TEAM = {"coach": "coachmaster", "atleta1": "golf2026"}

try:
    # 1. LETTURA FILE 1 (ALLENAMENTI)
    url_all_grezzo = st.secrets["connections"]["gsheets"]["url"]
    base_link_all = url_all_grezzo.split("/edit")[0] if "/edit" in url_all_grezzo else url_all_grezzo.split("?")[0].rstrip("/")
    csv_url_all = f"{base_link_all}/export?format=csv&nocache={int(time.time())}"
    df_completo = pd.read_csv(csv_url_all)
    df_completo.columns = df_completo.columns.str.strip()

    # 2. LETTURA FILE 2 (CREDENZIALI)
    try:
        url_cred_grezzo = st.secrets["connections"]["gsheets"]["url_credenziali"]
        base_link_cred = url_cred_grezzo.split("/edit")[0] if "/edit" in url_cred_grezzo else url_cred_grezzo.split("?")[0].rstrip("/")
        csv_url_cred = f"{base_link_cred}/export?format=csv&nocache={int(time.time())}&r={random.randint(1,9999)}"
        df_utenti = pd.read_csv(csv_url_cred)
        df_utenti.columns = df_utenti.columns.str.strip()
        if df_utenti.shape[1] >= 2:
            utenti_letti = dict(zip(
                df_utenti.iloc[:, 0].astype(str).str.lower().str.strip(),
                df_utenti.iloc[:, 1].astype(str).str.strip()
            ))
            UTENTI_TEAM.update(utenti_letti)
    except Exception as errore_cred:
        st.sidebar.warning(f"Controllo password online non attivo: {errore_cred}")

except Exception as e:
    st.error(f"Errore di configurazione: {e}")
    st.stop()

UTENTI_TEAM.update(st.session_state.nuovo_utente_locale)

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

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("## ⛳ Accesso Team")
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
                    st.error("Username di almeno 3 caratteri e password di almeno 4.")
                elif user_in in UTENTI_TEAM:
                    st.error("Questo username è già stato preso da un altro atleta.")
                else:
                    try:
                        url_script = st.secrets["connections"]["gsheets"]["script_url"]
                        payload_reg = {"azione": "registrazione", "utente": user_in, "password": pass_in}
                        res_reg = requests.post(url_script, data=json.dumps(payload_reg), headers={"Content-Type": "text/plain"}, allow_redirects=True)
                        res_data = res_reg.json() if res_reg.status_code == 200 else {}
                        if res_reg.status_code == 200 and res_data.get("status") != "exists":
                            st.session_state.nuovo_utente_locale[user_in] = pass_in
                            st.success("🎉 Profilo creato! Seleziona 'Accedi' sopra per entrare.")
                        else:
                            st.error("Impossibile registrarsi: l'utente esiste già online.")
                    except:
                        st.error("Errore di comunicazione durante la registrazione.")
    else:
        st.success(f"🌐 Utente: {st.session_state.username.lower()}")
        if st.button("🚪 Esci", use_container_width=True):
            st.session_state.autenticato, st.session_state.username = False, ""
            st.rerun()

# ---------- CORPO ----------
if not st.session_state.autenticato:
    hero("⛳ Golf Performance Hub", "Allenati, registra, migliora. Accedi dalla barra laterale per iniziare.")
else:
    is_coach = (st.session_state.username == "coach")
    col_utente = 'Utente' if 'Utente' in df_completo.columns else ('utente' if 'utente' in df_completo.columns else df_completo.columns[0])
    col_fase = 'Fase' if 'Fase' in df_completo.columns else ('fase' if 'fase' in df_completo.columns else df_completo.columns[1])
    col_diff = 'Difficoltà' if 'Difficoltà' in df_completo.columns else ('difficolta' if 'difficolta' in df_completo.columns else df_completo.columns[-1])

    if is_coach:
        hero("👨‍🏫 Pannello Coach", "Visione globale del team")
        elenco_atleti = ["Tutti"] + list(UTENTI_TEAM.keys())
        sel = st.selectbox("Seleziona atleta:", [a for a in elenco_atleti if a != "coach"])
        df_visibile = df_completo if sel == "Tutti" else df_completo[df_completo[col_utente].astype(str).str.lower().str.strip() == sel.lower().strip()]
    else:
        hero("⛳ Golf Performance Cloud", f"Ciao {st.session_state.username.capitalize()}, pronto per la sessione di oggi?")
        df_visibile = df_completo[df_completo[col_utente].astype(str).str.lower().str.strip() == st.session_state.username.lower().strip()]

    tab_inserimento, tab_dashboard = st.tabs(["📝 Inserisci Allenamento", "📊 Vedi Progressi"])

    with tab_inserimento:
        if is_coach:
            st.warning("I profili Coach monitorano i dati esclusivamente dalla tab 'Vedi Progressi'.")
        else:
            step(1, "Scegli la sessione")
            fasi = [("⚡ Pre Gara", "⚡", "PRE GARA", "#e0f2fe"),
                    ("🧘 Post Gara", "🧘", "POST GARA", "#dcfce7"),
                    ("🏠 Allenamento a Casa", "🏠", "A CASA", "#fef3c7")]
            for col, (chiave, ico, nome, colore) in zip(st.columns(3), fasi):
                with col:
                    attiva = "attiva" if st.session_state.fase_selezionata == chiave else ""
                    st.markdown(f'<div class="fase {attiva}" style="background:{colore}"><div class="ico">{ico}</div><b>{nome}</b></div>', unsafe_allow_html=True)
                    if st.button(f"Attiva {nome.title()}", use_container_width=True, key=f"fase_{chiave}",
                                 type="primary" if attiva else "secondary"):
                        st.session_state.fase_selezionata = chiave
                        st.rerun()

            st.write("")
            step(2, f"Esercizio svolto · {st.session_state.fase_selezionata}")
            col_es1, col_es2 = st.columns(2)
            for i, es in enumerate(DIZIONARIO_ESERCIZI[st.session_state.fase_selezionata]):
                with (col_es1 if i % 2 == 0 else col_es2):
                    if st.button(es, use_container_width=True, type="primary" if (st.session_state.esercizio_selezionato == es) else "secondary", key=f"btn_es_{i}"):
                        st.session_state.esercizio_selezionato = es
                        st.rerun()

            st.write("")
            step(3, f"Parametri · {st.session_state.esercizio_selezionato}")
            with st.container(border=True):
                cp1, cp2 = st.columns(2)
                with cp1:
                    serie = st.number_input("🔢 Serie:", min_value=1, value=3)
                    ripetizioni = st.number_input("🔄 Ripetizioni / Sec:", min_value=1, value=10)
                    carico = st.number_input("⚖️ Carico (Kg):", min_value=0.0, value=0.0, step=0.5)
                with cp2:
                    difficolta = st.slider("⭐ Fatica Percepita (RPE 1-5):", min_value=1, max_value=5, value=3)
                    impressioni = st.text_area("💭 Note e sensazioni:")

            if st.button("🚀 Sincronizza nel Cloud Team", use_container_width=True, type="primary"):
                try:
                    url_script = st.secrets["connections"]["gsheets"]["script_url"]
                    payload = {"azione": "allenamento", "utente": st.session_state.username, "fase": st.session_state.fase_selezionata, "categoria": "Sessione Diretta", "esercizio": st.session_state.esercizio_selezionato, "serie": int(serie), "ripetizioni": int(ripetizioni), "peso": float(carico), "difficolta": int(difficolta), "note": impressioni}
                    res = requests.post(url_script, data=json.dumps(payload), headers={"Content-Type": "text/plain"}, allow_redirects=True)
                    if res.status_code == 200:
                        st.balloons()
                        st.success("💪 Ottimo lavoro! Sessione salvata nel Cloud.")
                    else:
                        st.error(f"Errore di rete. Codice: {res.status_code}")
                except Exception as err:
                    st.error(f"Impossibile salvare: {err}")

    with tab_dashboard:
        t_col, r_col = st.columns([3, 1])
        with t_col:
            st.subheader("Carichi di lavoro live")
        with r_col:
            if st.button("🔄 Aggiorna Dati", use_container_width=True):
                st.rerun()

        if df_visibile.empty:
            st.info("Nessun dato registrato al momento nel database Cloud.")
        else:
            df_v = df_visibile.copy()
            k1, k2, k3 = st.columns(3)
            k1.metric("Esercizi totali", len(df_v))
            if col_diff in df_v.columns:
                df_v[col_diff] = pd.to_numeric(df_v[col_diff], errors='coerce')
                k2.metric("Fatica media", f"{df_v[col_diff].mean():.1f} / 5 ⭐")
            if col_fase in df_v.columns:
                k3.metric("Fase più allenata", str(df_v[col_fase].mode().iloc[0]))

            if col_fase in df_v.columns:
                st.markdown("#### Esercizi per fase")
                st.bar_chart(df_v[col_fase].value_counts(), color="#16a34a")
            if col_diff in df_v.columns and df_v[col_diff].notna().any():
                st.markdown("#### Andamento fatica percepita")
                st.line_chart(df_v[col_diff].reset_index(drop=True), color="#c9a227")

            with st.expander("📋 Tutti i dati", expanded=False):
                st.dataframe(df_v, use_container_width=True)
