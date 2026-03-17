# database.py
# GERENCIAMENTO DE BANCO DE DADOS COM FOCO EM LGPD
# Guardamos apenas o essencial: email, nome, controle de uso e assinatura
# NENHUMA senha é armazenada (login via Google OAuth)
# Fácil de implementar exclusão de dados se o usuário solicitar

import sqlite3
from datetime import datetime, date
import streamlit as st
import os

DATABASE_PATH = "safira.db"

def get_connection():
    """Retorna conexão com o banco SQLite"""
    return sqlite3.connect(DATABASE_PATH)

def init_database():
    """Cria a tabela de usuários se não existir"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabela com campos mínimos necessários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            email TEXT PRIMARY KEY,              -- Identificador único (LGPD: dado pessoal)
            nome TEXT,                           -- Apenas para personalização (LGPD: dado pessoal)
            usos_hoje INTEGER DEFAULT 0,          -- Controle de limite gratuito
            data_ultimo_uso DATE,                  -- Para resetar contador diário
            assinante BOOLEAN DEFAULT 0,           -- TRUE se tem plano ilimitado
            assinatura_valida_ate DATE,            -- Opcional: data de expiração
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Metadado interno
        )
    ''')
    
    conn.commit()
    conn.close()

def get_usuario(email):
    """Retorna dados do usuário ou None se não existir"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT email, nome, usos_hoje, data_ultimo_uso, assinante, assinatura_valida_ate FROM usuarios WHERE email = ?",
        (email,)
    )
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "email": row[0],
            "nome": row[1],
            "usos_hoje": row[2],
            "data_ultimo_uso": row[3],
            "assinante": bool(row[4]),
            "assinatura_valida_ate": row[5]
        }
    return None

def criar_ou_atualizar_usuario(email, nome):
    """
    Cria usuário se não existir, ou atualiza o nome se já existir.
    Respeita LGPD: só armazena o necessário.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verifica se já existe
    existe = cursor.execute("SELECT 1 FROM usuarios WHERE email = ?", (email,)).fetchone()
    
    hoje = date.today().isoformat()
    
    if existe:
        # Atualiza apenas o nome (pode ter mudado no Google)
        cursor.execute(
            "UPDATE usuarios SET nome = ? WHERE email = ?",
            (nome, email)
        )
    else:
        # Insere novo usuário com contador zerado
        cursor.execute(
            "INSERT INTO usuarios (email, nome, usos_hoje, data_ultimo_uso, assinante) VALUES (?, ?, 0, ?, 0)",
            (email, nome, hoje)
        )
    
    conn.commit()
    conn.close()

def pode_usar(email):
    """
    Verifica se o usuário pode fazer uma análise hoje.
    Retorna (bool, mensagem, usos_restantes)
    """
    usuario = get_usuario(email)
    if not usuario:
        return False, "Usuário não encontrado", 0
    
    hoje = date.today()
    data_ultimo_uso = usuario["data_ultimo_uso"]
    
    # Se é assinante, sempre pode
    if usuario["assinante"]:
        # Verifica se assinatura expirou (se tiver data)
        if usuario["assinatura_valida_ate"]:
            valida_ate = date.fromisoformat(usuario["assinatura_valida_ate"])
            if hoje > valida_ate:
                # Assinatura expirada, trata como não assinante
                usuario["assinante"] = False
            else:
                return True, "Assinante ativo", 999
        
        if usuario["assinante"]:
            return True, "Assinante ativo", 999
    
    # Não assinante: verifica limite diário
    if data_ultimo_uso and date.fromisoformat(data_ultimo_uso) == hoje:
        usos = usuario["usos_hoje"]
        restantes = max(0, 5 - usos)
        if usos >= 5:
            return False, "Limite diário atingido (5/5). Assine para uso ilimitado.", 0
        return True, f"Uso gratuito: {usos}/5 hoje", restantes
    else:
        # Primeiro uso do dia
        return True, "Primeiro uso do dia (0/5)", 5

def registrar_uso(email):
    """
    Incrementa o contador de uso do usuário.
    Se for um novo dia, reseta o contador para 1.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    hoje = date.today().isoformat()
    
    # Busca dados atuais
    cursor.execute(
        "SELECT usos_hoje, data_ultimo_uso FROM usuarios WHERE email = ?",
        (email,)
    )
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return
    
    usos_hoje, data_ultimo_uso = row
    
    # Se é um novo dia, reseta o contador
    if data_ultimo_uso != hoje:
        usos_hoje = 1
        data_ultimo_uso = hoje
    else:
        usos_hoje += 1
    
    # Atualiza
    cursor.execute(
        "UPDATE usuarios SET usos_hoje = ?, data_ultimo_uso = ? WHERE email = ?",
        (usos_hoje, data_ultimo_uso, email)
    )
    
    conn.commit()
    conn.close()

def tornar_assinante(email, dias=30):
    """
    Marca usuário como assinante por X dias.
    Útil para quando você receber a confirmação de pagamento.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    hoje = date.today()
    valida_ate = (hoje + timedelta(days=dias)).isoformat()
    
    cursor.execute(
        "UPDATE usuarios SET assinante = 1, assinatura_valida_ate = ? WHERE email = ?",
        (valida_ate, email)
    )
    
    conn.commit()
    conn.close()
    
    st.success(f"✅ Usuário {email} agora é assinante até {valida_ate}")

def excluir_usuario(email):
    """
    Função para cumprir LGPD: direito ao esquecimento.
    Remove todos os dados do usuário do banco.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM usuarios WHERE email = ?", (email,))
    
    conn.commit()
    conn.close()
    
    return True

# Inicializa o banco ao importar o módulo
init_database()