import streamlit as st
import sqlite3
import pandas as pd
import time
from datetime import datetime

# --- 1. Configuração da Página ---
st.set_page_config(page_title="Tracker Pós-Cirúrgico", page_icon="👁️", layout="centered")

# --- 2. Configuração do Banco de Dados (SQLite) ---
def init_db():
    conn = sqlite3.connect('estudos.db')
    c = conn.cursor()
    # Cria tabela se não existir
    c.execute('''
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            materia TEXT,
            energia INTEGER,
            notas TEXT
        )
    ''')
    conn.commit()
    conn.close()

def salvar_no_bd(materia, energia, notas):
    conn = sqlite3.connect('estudos.db')
    c = conn.cursor()
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('INSERT INTO historico (data, materia, energia, notas) VALUES (?, ?, ?, ?)',
              (data_hora, materia, energia, notas))
    conn.commit()
    conn.close()

def ler_bd():
    conn = sqlite3.connect('estudos.db')
    df = pd.read_sql_query("SELECT * FROM historico ORDER BY id DESC", conn)
    conn.close()
    return df

# Inicializa o banco ao abrir
init_db()

# --- 3. Estilos CSS (Modo Escuro e Fontes Grandes) ---
st.markdown("""
    <style>
    /* Aumentar fonte do timer */
    .big-timer {
        font-size: 80px !important;
        font-weight: bold;
        color: #00ff88;
        text-align: center;
        margin-bottom: 0px;
    }
    .status-text {
        font-size: 20px;
        color: #888;
        text-align: center;
        margin-bottom: 20px;
    }
    /* Botões grandes */
    .stButton button {
        height: 3em;
        width: 100%;
        font-size: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. Lógica do Timer ---
if 'tempo_restante' not in st.session_state:
    st.session_state.tempo_restante = 20 * 60  # 20 minutos
if 'rodando' not in st.session_state:
    st.session_state.rodando = False
if 'modo' not in st.session_state:
    st.session_state.modo = "FOCO"  # ou DESCANSO

st.title("👁️ Tracker de Recuperação")

# Container do Timer
placeholder = st.empty()
btn_col1, btn_col2 = st.columns(2)

# Botão Iniciar/Pausar
with btn_col1:
    label_btn = "⏸️ PAUSAR" if st.session_state.rodando else "▶️ INICIAR"
    if st.button(label_btn):
        st.session_state.rodando = not st.session_state.rodando

# Botão Alternar Modo
with btn_col2:
    novo_modo = "👁️ DESCANSO" if st.session_state.modo == "FOCO" else "🧠 FOCO"
    if st.button(f"Mudar para {novo_modo}"):
        st.session_state.modo = "DESCANSO" if st.session_state.modo == "FOCO" else "FOCO"
        st.session_state.tempo_restante = 20 * 60
        st.session_state.rodando = False
        st.rerun()

# Loop do Timer
while st.session_state.rodando and st.session_state.tempo_restante > 0:
    mins, secs = divmod(st.session_state.tempo_restante, 60)
    timer_fmt = f"{mins:02d}:{secs:02d}"
    
    # Atualiza visualização
    cor = "#00ff88" if st.session_state.modo == "FOCO" else "#00d2ff"
    msg = "MODO ESTUDO" if st.session_state.modo == "FOCO" else "DESCANSO VISUAL (Olhe longe)"
    
    placeholder.markdown(f"""
        <div class='big-timer' style='color:{cor}'>{timer_fmt}</div>
        <div class='status-text'>{msg}</div>
        """, unsafe_allow_html=True)
    
    time.sleep(1)
    st.session_state.tempo_restante -= 1
    
    # Se chegar a zero
    if st.session_state.tempo_restante == 0:
        st.session_state.rodando = False
        st.balloons()
        st.rerun()

# Mostra timer parado se não estiver rodando
if not st.session_state.rodando:
    mins, secs = divmod(st.session_state.tempo_restante, 60)
    timer_fmt = f"{mins:02d}:{secs:02d}"
    cor = "#00ff88" if st.session_state.modo == "FOCO" else "#00d2ff"
    msg = "PAUSADO"
    placeholder.markdown(f"""
        <div class='big-timer' style='color:{cor}'>{timer_fmt}</div>
        <div class='status-text'>{msg}</div>
        """, unsafe_allow_html=True)

# --- 5. Área de Registro (SQLite) ---
st.divider()
st.subheader("📝 Registrar Bloco")

with st.form("log_form"):
    c1, c2 = st.columns(2)
    materia = c1.text_input("Matéria")
    energia = c2.slider("Nível Energia (Pós-Bupropiona)", 1, 5, 3)
    notas = st.text_area("Notas rápidas")
    
    if st.form_submit_button("Salvar no Banco de Dados"):
        salvar_no_bd(materia, energia, notas)
        st.success("Salvo com sucesso!")
        time.sleep(1)
        st.rerun()

# --- 6. Histórico ---
st.divider()
st.subheader("📊 Histórico Salvo")
df = ler_bd()
if not df.empty:
    st.dataframe(df, use_container_width=True)
    
    # Botão para baixar CSV (Backup)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Baixar Backup CSV", csv, "historico.csv", "text/csv")
else:
    st.info("Nenhum registro no banco de dados ainda.")
