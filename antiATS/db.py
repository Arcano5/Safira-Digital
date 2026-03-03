# db.py
import mysql.connector
import streamlit as st
from datetime import date, datetime
import pandas as pd

# === CONEXÃO ===
def get_connection(mysql_password):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=mysql_password,
            database="sistema_leonor"
        )
        return conn
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return None

# === INICIALIZAÇÃO ===
def inicializar_banco(mysql_password):
    if not mysql_password:
        return False
    
    try:
        conn = get_connection(mysql_password)
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                google_id VARCHAR(255) UNIQUE,
                email VARCHAR(255) UNIQUE,
                nome VARCHAR(255),
                foto TEXT,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ultimo_login TIMESTAMP NULL,
                uso_count INT DEFAULT 0,
                uso_reset DATE DEFAULT (CURRENT_DATE),
                newsletter BOOLEAN DEFAULT FALSE,
                newsletter_consent_date TIMESTAMP NULL,
                newsletter_consent_ip VARCHAR(45),
                plano ENUM('free', 'premium', 'carreira') DEFAULT 'free',
                assinatura_inicio DATE NULL,
                assinatura_fim DATE NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analises (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT,
                titulo_vaga VARCHAR(255),
                empresa VARCHAR(255),
                data_analise TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                hard_skills TEXT,
                soft_skills TEXT,
                percentual_match INT,
                habilidades_faltantes TEXT,
                plano_7_dias TEXT,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS minhas_analises (
                id INT AUTO_INCREMENT PRIMARY KEY,
                titulo_vaga VARCHAR(255),
                empresa VARCHAR(255),
                data_analise TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                hard_skills TEXT,
                soft_skills TEXT,
                percentual_match INT,
                skills_faltantes TEXT
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        st.error(f"Erro ao inicializar banco: {e}")
        return False

# === USUÁRIOS ===
def salvar_usuario_google(user_data, mysql_password):
    try:
        conn = get_connection(mysql_password)
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, uso_count, uso_reset FROM usuarios WHERE google_id = %s", (user_data['id'],))
        existing = cursor.fetchone()
        
        if existing:
            user_id, uso_count, uso_reset = existing
            
            if uso_reset < date.today():
                cursor.execute("""
                    UPDATE usuarios 
                    SET uso_count = 0, uso_reset = %s, ultimo_login = NOW() 
                    WHERE id = %s
                """, (date.today(), user_id))
                uso_count = 0
            else:
                cursor.execute("UPDATE usuarios SET ultimo_login = NOW() WHERE id = %s", (user_id,))
            
            conn.commit()
            
        else:
            cursor.execute("""
                INSERT INTO usuarios 
                (google_id, email, nome, foto, ultimo_login, uso_reset) 
                VALUES (%s, %s, %s, %s, NOW(), %s)
            """, (
                user_data['id'],
                user_data['email'],
                user_data['name'],
                user_data['picture'],
                date.today()
            ))
            user_id = cursor.lastrowid
            conn.commit()
            uso_count = 0
        
        cursor.close()
        conn.close()
        
        return {
            'success': True,
            'user_id': user_id,
            'email': user_data['email'],
            'nome': user_data['name'],
            'foto': user_data['picture'],
            'uso_count': uso_count
        }
        
    except Exception as e:
        st.error(f"Erro ao salvar usuário: {e}")
        return {'success': False}

# === CONTROLE DE USO ===
def verificar_limite_uso(user_id, mysql_password, admin_autenticado=False):
    if admin_autenticado:
        return True, 0, "admin", "admin"
    
    if not user_id:
        return True, 0, "anonimo", "free"
    
    try:
        conn = get_connection(mysql_password)
        if not conn:
            return True, 0, "logado", "free"
            
        cursor = conn.cursor()
        cursor.execute("""
            SELECT uso_count, uso_reset, plano 
            FROM usuarios 
            WHERE id = %s
        """, (user_id,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            uso_count, uso_reset, plano = result
            
            if uso_reset < date.today():
                uso_count = 0
                conn = get_connection(mysql_password)
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE usuarios 
                    SET uso_count = 0, uso_reset = %s 
                    WHERE id = %s
                """, (date.today(), user_id))
                conn.commit()
                cursor.close()
                conn.close()
            
            limite = 3 if plano == 'free' else 999999
            
            if uso_count >= limite:
                return False, uso_count, "logado", plano
            
            return True, uso_count, "logado", plano
        else:
            return True, 0, "logado", "free"
            
    except Exception as e:
        st.error(f"Erro ao verificar uso: {e}")
        return True, 0, "logado", "free"

def incrementar_uso(user_id, mysql_password):
    if not user_id:
        return False
    
    try:
        conn = get_connection(mysql_password)
        if not conn:
            return False
            
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE usuarios 
            SET uso_count = uso_count + 1 
            WHERE id = %s
        """, (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        st.error(f"Erro ao incrementar uso: {e}")
        return False

# === ANÁLISES ===
def salvar_analise_usuario(user_id, titulo, empresa, resultado, mysql_password):
    if not user_id:
        return False
    
    try:
        conn = get_connection(mysql_password)
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        sql = """
            INSERT INTO analises 
            (usuario_id, titulo_vaga, empresa, hard_skills, soft_skills, percentual_match, habilidades_faltantes, plano_7_dias) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (
            user_id,
            titulo,
            empresa,
            resultado.get("hard_skills", "")[:500],
            resultado.get("soft_skills", "")[:500],
            resultado.get("percentual_match", 0),
            resultado.get("habilidades_faltantes", "")[:500],
            resultado.get("plano_7_dias", "")[:1000]
        )
        
        cursor.execute(sql, valores)
        conn.commit()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        st.error(f"Erro ao salvar análise: {e}")
        return False

def salvar_analise_admin(titulo, empresa, resultado, mysql_password):
    try:
        conn = get_connection(mysql_password)
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO minhas_analises 
            (titulo_vaga, empresa, hard_skills, soft_skills, percentual_match, skills_faltantes) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            titulo, empresa,
            resultado.get("hard_skills", "")[:500],
            resultado.get("soft_skills", "")[:500],
            resultado.get("percentual_match", 0),
            resultado.get("habilidades_faltantes", "")[:500]
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        st.error(f"Erro ao salvar para admin: {e}")
        return False

# === NEWSLETTER ===
def atualizar_newsletter(user_id, opt_in, mysql_password, ip="127.0.0.1"):
    if not user_id:
        return False
    
    try:
        conn = get_connection(mysql_password)
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        if opt_in:
            cursor.execute("""
                UPDATE usuarios 
                SET newsletter = TRUE, 
                    newsletter_consent_date = NOW(), 
                    newsletter_consent_ip = %s 
                WHERE id = %s
            """, (ip, user_id))
        else:
            cursor.execute("""
                UPDATE usuarios 
                SET newsletter = FALSE 
                WHERE id = %s
            """, (user_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        st.error(f"Erro ao atualizar newsletter: {e}")
        return False