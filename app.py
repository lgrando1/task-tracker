import streamlit as st
import sqlite3
import pandas as pd
import time
import random
import os
from datetime import datetime

# --- 1. Configuração da Página ---
st.set_page_config(page_title="Tracker Feynman", page_icon="🎓", layout="centered")

# NOME DO ARQUIVO DO BANCO DE DADOS (Mudamos o nome para forçar criação de um novo)
DB_FILE = 'feynman_v2.db'

# --- 2. Banco de Dados ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Cria tabela com a estrutura nova
    c.execute('''
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            materia TEXT,
            energia INTEGER,
            tipo_estudo TEXT,
            feynman_explicacao TEXT
        )
    ''')
    conn.commit()
    conn.close()

def salvar_no_bd(materia, energia, tipo, explicacao):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('''
            INSERT INTO historico (data, materia, energia, tipo_estudo, feynman_explicacao) 
            VALUES (?, ?, ?, ?, ?)
        ''', (data_hora, materia, energia, tipo, explicacao))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
        return False

def ler_bd():
    if not os.path.exists(DB_FILE):
        return pd.DataFrame()
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM historico ORDER BY id DESC", conn)
    conn.close()
    return df

# Inicializa o banco
init_db()

# --- 3. CSS para Acessibilidade Visual ---
st.markdown("""
    <style>
    .big-timer { font-size: 80px !important; font-weight: bold; color: #00ff88; text-align: center; }
    .status-text { font-size: 24px; color: #ccc; text-align: center; margin-bottom: 20px; }
    .feynman-box { border: 2px solid #00ff88; padding: 20px; border-radius: 10px; background-color: #111; }
    .stTextArea textarea { font-size: 18px !important; line-height: 1.5; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. Sidebar (Controle de Emergência) ---
with st.sidebar:
    st.header("⚙️ Configurações")
    st.info("Se o app der erro de banco de dados, clique abaixo para resetar.")
    if st.button("⚠️ DELETAR BANCO DE DADOS"):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
            st.warning("Banco deletado! Recarregue a página.")
            time.sleep(2)
            st.rerun()
        else:
            st.write("Nenhum banco encontrado.")

# --- 5. Lógica do Timer e Estado ---
if 'tempo_restante' not in st.session_state: st.session_state.tempo_restante = 20 * 60
if 'rodando' not in st.session_state: st.session_state.rodando = False
if 'modo' not in st.session_state: st.session_state.modo = "ABSORÇÃO (Input)"

# --- Interface Principal ---
st.title("🎓 Tracker Feynman: Áudio & Fala")

# Timer Grande
col_timer, col_ctrl = st.columns([2, 1])
with col_timer:
    mins, secs = divmod(st.session_state.tempo_restante, 60)
    cor = "#00ff88" if "ABSORÇÃO" in st.session_state.modo else "#ffcc00" # Amarelo para Feynman
    st.markdown(f"<div class='big-timer' style='color:{cor}'>{mins:02d}:{secs:02d}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='status-text'>{st.session_state.modo}</div>", unsafe_allow_html=True)

with col_ctrl:
    st.write("##") # Espaçamento
    if st.button("⏯️ INICIAR / PAUSAR", use_container_width=True):
        st.session_state.rodando = not st.session_state.rodando
    
    # Botão para alternar fases da técnica Feynman
    if st.button("🔄 TROCAR FASE", use_container_width=True):
        fases = ["🎧 ABSORÇÃO (Ouvir)", "🗣️ FEYNMAN (Explicar)", "👁️ DESCANSO"]
        atual = st.session_state.modo
        # Lógica simples de ciclo
        if "ABSORÇÃO" in atual: st.session_state.modo = fases[1]
        elif "FEYNMAN" in atual: st.session_state.modo = fases[2]
        else: st.session_state.modo = fases[0]
        
        st.session_state.tempo_restante = 20 * 60
        st.session_state.rodando = False
        st.rerun()

# Lógica de contagem
if st.session_state.rodando and st.session_state.tempo_restante > 0:
    time.sleep(1)
    st.session_state.tempo_restante -= 1
    st.rerun()
elif st.session_state.rodando and st.session_state.tempo_restante == 0:
    st.balloons()
    st.session_state.rodando = False

# --- 6. O Módulo Feynman ---
st.divider()

if "FEYNMAN" in st.session_state.modo:
    st.markdown("<div class='feynman-box'>", unsafe_allow_html=True)
    st.subheader("🗣️ Momento da Aula (Ditado)")
    
    prompts = [
        "Como você explicaria isso para sua avó?",
        "Explique isso sem usar as palavras técnicas principais.",
        "Crie uma analogia com algo do cotidiano.",
        "Onde um aluno iniciante ficaria confuso aqui?"
    ]
    if 'prompt_atual' not in st.session_state:
        st.session_state.prompt_atual = random.choice(prompts)
    
    st.info(f"💡 **Desafio:** {st.session_state.prompt_atual}")
    if st.button("🎲 Novo Desafio"):
        st.session_state.prompt_atual = random.choice(prompts)
    
    st.markdown("</div>", unsafe_allow_html=True)

# --- 7. Formulário de Registro Unificado ---
with st.form("log_feynman"):
    st.write("### 📝 Registrar Ciclo")
    c1, c2 = st.columns(2)
    materia = c1.text_input("Tópico Estudado")
    energia = c2.slider("Energia", 1, 5, 3)
    
    # Campo principal para a técnica
    explicacao = st.text_area(
        "Sua Explicação Simplificada (Use o Ditado)", 
        height=150,
        placeholder="Clique no microfone do teclado e comece a falar..."
    )
    
    if st.form_submit_button("Salvar no Histórico"):
        if salvar_no_bd(materia, energia, st.session_state.modo, explicacao):
            st.success("Progresso registrado!")
            time.sleep(1)
            st.rerun()

# --- 8. Visualização Rápida ---
with st.expander("📚 Ver Explicações Anteriores"):
    df = ler_bd()
    if not df.empty:
        # Botão de download
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar tudo (CSV)", csv, "feynman_backup.csv", "text/csv")
        
        for index, row in df.iterrows():
            st.markdown(f"**{row['data']} - {row['materia']}** (Energia: {row['energia']})")
            st.info(f"🗣️ *{row['feynman_explicacao']}*")
            st.write("---")
