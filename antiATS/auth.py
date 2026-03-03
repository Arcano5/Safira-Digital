# auth.py
import streamlit as st
import secrets
import urllib.parse
import requests
from db import salvar_usuario_google

def gerar_estado():
    if 'oauth_state' not in st.session_state:
        st.session_state['oauth_state'] = secrets.token_urlsafe(32)
    return st.session_state['oauth_state']

def gerar_url_google(app_url, google_client_id):
    state = gerar_estado()
    
    params = {
        'client_id': google_client_id,
        'redirect_uri': f"{app_url}/oauth2callback",
        'response_type': 'code',
        'scope': 'email profile',
        'access_type': 'offline',
        'state': state,
        'prompt': 'consent'
    }
    
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    return url

def trocar_codigo_google(code, app_url, google_client_id, google_client_secret):
    try:
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            'code': code,
            'client_id': google_client_id,
            'client_secret': google_client_secret,
            'redirect_uri': f"{app_url}/oauth2callback",
            'grant_type': 'authorization_code'
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_json = token_response.json()
        
        if 'access_token' not in token_json:
            st.error(f"Erro no token: {token_json.get('error', 'Desconhecido')}")
            return None
        
        user_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {'Authorization': f"Bearer {token_json['access_token']}"}
        user_response = requests.get(user_url, headers=headers)
        user_data = user_response.json()
        
        if 'error' in user_data:
            st.error(f"Erro ao obter usuário: {user_data['error']}")
            return None
        
        return {
            'id': user_data['id'],
            'email': user_data['email'],
            'name': user_data.get('name', ''),
            'picture': user_data.get('picture', ''),
            'provider': 'google'
        }
        
    except Exception as e:
        st.error(f"Erro na autenticação Google: {e}")
        return None

def verificar_callback_google(app_url, google_client_id, google_client_secret, mysql_password):
    query_params = st.query_params
    
    if 'code' in query_params and 'state' in query_params:
        code = query_params['code']
        state = query_params['state']
        
        if state != st.session_state.get('oauth_state', ''):
            st.error("Erro de segurança: estado inválido")
            return False
        
        user_data = trocar_codigo_google(code, app_url, google_client_id, google_client_secret)
        
        if user_data:
            resultado = salvar_usuario_google(user_data, mysql_password)
            if resultado and resultado['success']:
                st.session_state['user_id'] = resultado['user_id']
                st.session_state['user_email'] = resultado['email']
                st.session_state['user_name'] = resultado['nome']
                st.session_state['user_picture'] = resultado['foto']
                st.session_state['authenticated'] = True
                st.session_state['uso_count'] = resultado['uso_count']
                st.success("✅ Login realizado com sucesso!")
                st.query_params.clear()
                if 'oauth_state' in st.session_state:
                    del st.session_state['oauth_state']
                st.rerun()
                return True
    
    return False

def fazer_logout():
    keys = ['user_id', 'user_email', 'user_name', 'user_picture', 'authenticated', 'uso_count']
    for key in keys:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

def autenticar_admin(admin_password):
    with st.sidebar.expander("🔐 Área Admin", expanded=False):
        senha = st.text_input("Senha de admin", type="password", key="admin_senha")
        if st.button("Entrar", key="admin_entrar"):
            if senha == admin_password:
                st.session_state['admin_autenticado'] = True
                st.success("✅ Acesso concedido!")
                st.rerun()
            else:
                st.error("❌ Senha incorreta")
        
        if st.session_state.get('admin_autenticado', False):
            st.success("✅ Admin logado")
            if st.button("Sair", key="admin_sair"):
                st.session_state['admin_autenticado'] = False
                st.rerun()
    
    return st.session_state.get('admin_autenticado', False)