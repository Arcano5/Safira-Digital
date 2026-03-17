# auth_google.py
# AUTENTICAÇÃO GOOGLE OAUTH2 FUNCIONAL
# Baseado na RFC 6749 (OAuth 2.0)
# Usa flow de Authorization Code com PKCE para maior segurança

import streamlit as st
import requests
import urllib.parse
import secrets
import hashlib
import base64
from database import criar_ou_atualizar_usuario
import time

def gerar_code_verifier():
    """Gera um code_verifier para PKCE (RFC 7636)"""
    return secrets.token_urlsafe(64)

def gerar_code_challenge(verifier):
    """Gera code_challenge a partir do verifier (SHA256)"""
    sha256 = hashlib.sha256(verifier.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(sha256).decode('utf-8').rstrip('=')

def gerar_estado():
    """Gera estado para proteção CSRF"""
    if 'oauth_state' not in st.session_state:
        st.session_state['oauth_state'] = secrets.token_urlsafe(32)
    return st.session_state['oauth_state']

def get_secret(key, default=None):
    """Tenta pegar de st.secrets, depois .env"""
    try:
        return st.secrets.get(key, default)
    except:
        from dotenv import load_dotenv
        import os
        load_dotenv()
        return os.getenv(key, default)

def gerar_url_google():
    """Gera URL de autorização do Google com PKCE"""
    
    # Carrega credenciais dos secrets
    google_client_id = get_secret("GOOGLE_CLIENT_ID")
    app_url = get_secret("APP_URL", "http://localhost:8501")
    
    if not google_client_id:
        st.error("❌ GOOGLE_CLIENT_ID não configurado nos secrets")
        return "#"
    
    # Gera code_verifier e guarda na sessão
    code_verifier = gerar_code_verifier()
    st.session_state['code_verifier'] = code_verifier
    code_challenge = gerar_code_challenge(code_verifier)
    
    params = {
        'client_id': google_client_id,
        'redirect_uri': f"{app_url}/oauth2callback",
        'response_type': 'code',
        'scope': 'openid email profile',
        'state': gerar_estado(),
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256',
        'access_type': 'offline',
        'prompt': 'consent'
    }
    
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    return url

def processar_callback():
    """
    Processa o callback do Google OAuth.
    Retorna True se login bem-sucedido, False caso contrário.
    """
    
    # Verifica se tem parâmetros na URL
    if 'code' not in st.query_params:
        return False
    
    # Verifica estado para prevenir CSRF
    estado_recebido = st.query_params.get('state')
    estado_esperado = st.session_state.get('oauth_state')
    
    # Se for lista, pega o primeiro elemento
    if isinstance(estado_recebido, list):
        estado_recebido = estado_recebido[0]
    
    if not estado_esperado or estado_recebido != estado_esperado:
        st.error("❌ Erro de segurança: estado inválido")
        st.query_params.clear()
        return False
    
    # Pega o código e code_verifier
    code = st.query_params['code']
    if isinstance(code, list):
        code = code[0]
    
    code_verifier = st.session_state.get('code_verifier')
    
    if not code_verifier:
        st.error("❌ code_verifier não encontrado na sessão")
        return False
    
    # Carrega credenciais
    google_client_id = st.secrets.get("GOOGLE_CLIENT_ID")
    google_client_secret = st.secrets.get("GOOGLE_CLIENT_SECRET")
    app_url = st.secrets.get("APP_URL", "http://localhost:8501")
    
    # Troca o código por tokens
    token_url = "https://oauth2.googleapis.com/token"
    
    data = {
        'code': code,
        'client_id': google_client_id,
        'client_secret': google_client_secret,
        'redirect_uri': f"{app_url}/oauth2callback",
        'grant_type': 'authorization_code',
        'code_verifier': code_verifier
    }
    
    try:
        response = requests.post(token_url, data=data, timeout=10)
        if response.status_code != 200:
            st.error(f"❌ Erro ao obter token: {response.text}")
            return False
        
        tokens = response.json()
        
        # Obtém informações do usuário com o access_token
        userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {'Authorization': f"Bearer {tokens['access_token']}"}
        
        user_response = requests.get(userinfo_url, headers=headers, timeout=10)
        
        if user_response.status_code != 200:
            st.error("❌ Erro ao obter dados do usuário")
            return False
        
        user_data = user_response.json()
        
        # Salva no banco de dados
        email = user_data.get('email')
        nome = user_data.get('name', email.split('@')[0] if email else "Usuário")
        
        if email:
            criar_ou_atualizar_usuario(email, nome)
            
            # Guarda na sessão
            st.session_state['usuario'] = {
                'email': email,
                'nome': nome,
                'logado': True,
                'login_time': time.time()
            }
            
            # Limpa parâmetros da URL
            st.query_params.clear()
            
            # Remove code_verifier da sessão (já usado)
            if 'code_verifier' in st.session_state:
                del st.session_state['code_verifier']
            
            st.success(f"✅ Bem-vindo, {nome}!")
            return True
        else:
            st.error("❌ Email não obtido do Google")
            return False
        
    except Exception as e:
        st.error(f"❌ Erro no login: {str(e)}")
        return False

def fazer_logout():
    """Limpa a sessão e faz logout"""
    if 'usuario' in st.session_state:
        del st.session_state['usuario']
    if 'oauth_state' in st.session_state:
        del st.session_state['oauth_state']
    if 'code_verifier' in st.session_state:
        del st.session_state['code_verifier']
    st.rerun()

def mostrar_tela_login():
    """Exibe a tela de login com botão Google"""
    
    st.markdown("""
    <div style="text-align: center; padding: 3rem 1rem;">
        <h1>💎 Safira Digital</h1>
        <h3>Análise Anti-ATS</h3>
        <p style="margin: 2rem 0; color: #4A5568;">
            Faça login com sua conta Google para continuar<br>
            <small>🔒 Apenas e-mail e nome são armazenados (LGPD)</small>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    url_google = gerar_url_google()
    
    if url_google != "#":
        st.markdown(f"""
        <div style="text-align: center;">
            <a href="{url_google}" target="_self">
                <button style="
                    background: white;
                    color: #1E2B3F;
                    border: 2px solid #0A2472;
                    border-radius: 8px;
                    padding: 0.75rem 2rem;
                    font-size: 1.1rem;
                    font-weight: 600;
                    cursor: pointer;
                    display: inline-flex;
                    align-items: center;
                    gap: 0.5rem;
                    transition: all 0.3s;
                ">
                    <img src="https://www.google.com/favicon.ico" width="20" style="margin-right: 8px;">
                    Continuar com Google
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("🔧 Erro na configuração do login. Contate o administrador.")