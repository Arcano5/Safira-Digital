# auth_simple.py - Versão sem banco de dados
import streamlit as st
import secrets
import urllib.parse

def gerar_estado():
    if 'oauth_state' not in st.session_state:
        st.session_state['oauth_state'] = secrets.token_urlsafe(32)
    return st.session_state['oauth_state']

def gerar_url_google(app_url, google_client_id):
    if not google_client_id:
        return "#"
    
    params = {
        'client_id': google_client_id,
        'redirect_uri': f"{app_url}/oauth2callback",
        'response_type': 'code',
        'scope': 'email profile',
        'state': gerar_estado()
    }
    return "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)

def verificar_callback_google(app_url, google_client_id, google_client_secret, mysql_password=None):
    if 'code' in st.query_params:
        st.query_params.clear()
        st.info("Login Google desativado no modo teste")
    return False

def fazer_logout():
    st.session_state.clear()
    st.rerun()