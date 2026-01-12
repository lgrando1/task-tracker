import streamlit as st
import sqlite3
import pandas as pd
import time
import random
from datetime import datetime

# --- 1. Configuração da Página ---
st.set_page_config(page_title="Tracker Feynman", page_icon="🎓", layout="centered")

# --- 2. Banco de Dados (Com campo para o Método Feynman) ---
def init_db():
    conn = sqlite3.connect('estudos.db')
    c = conn.cursor()
    # Adicionamos a coluna 'feynman_explicacao'
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
    conn = sqlite3.connect('estudos.db')
    c = conn.cursor()
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        INSERT INTO historico (data, materia, energia, tipo_estudo, feynman_explicacao) 
        VALUES (?, ?, ?, ?, ?)
    ''', (data_hora, materia, energia, tipo, explicacao))
    conn.commit()
    conn.close()

def ler_bd():
    conn = sqlite3.connect('estudos.db')
    df = pd.read_sql_query("SELECT * FROM historico ORDER BY id DESC", conn)
    conn.close()
    return df

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

# --- 4. Lógica do Timer e Estado ---
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

# --- 5. O Módulo Feynman (Aparece sempre, mas destaque na fase de explicação) ---
st.divider()

if "FEYNMAN" in st.session_state.modo:
    st.markdown("<div class='feynman-box'>", unsafe_allow_html=True)
    st.subheader("🗣️ Momento da Aula (Ditado)")
    
    # Prompts aleatórios para estimular a explicação
    prompts = [
        "Como você explicaria isso para sua avó?",
        "Explique isso sem usar as palavras técnicas principais.",
        "Crie uma analogia com algo do cotidiano (comida, trânsito, futebol).",
        "Onde um aluno iniciante ficaria confuso aqui?"
    ]
    if 'prompt_atual' not in st.session_state:
        st.session_state.prompt_atual = random.choice(prompts)
    
    st.info(f"💡 **Desafio:** {st.session_state.prompt_atual}")
    if st.button("🎲 Novo Desafio"):
        st.session_state.prompt_atual = random.choice(prompts)
    
    st.markdown("</div>", unsafe_allow_html=True)

# --- 6. Formulário de Registro Unificado ---
with st.form("log_feynman"):
    st.write("### 📝 Registrar Ciclo")
    c1, c2 = st.columns(2)
    materia = c1.text_input("Tópico Estudado")
    energia = c2.slider("Energia", 1, 5, 3)
    
    # Campo principal para a técnica
    explicacao = st.text_area(
        "Sua Explicação Simplificada (Use o Ditado)", 
        height=150,
        placeholder="Clique no microfone do teclado e comece a falar: 'Basicamente, este conceito funciona como...'"
    )
    
    if st.form_submit_button("Salvar no Histórico"):
        salvar_no_bd(materia, energia, st.session_state.modo, explicacao)
        st.success("Progresso registrado!")

# --- 7. Visualização Rápida ---
with st.expander("📚 Ver Explicações Anteriores"):
    df = ler_bd()
    if not df.empty:
        for index, row in df.iterrows():
            st.markdown(f"**{row['data']} - {row['materia']}** (Energia: {row['energia']})")
            st.info(f"🗣️ *{row['feynman_explicacao']}*")
            st.write("---")
