# webhook.py
# Recebe notificações do Mercado Pago e libera acesso
import streamlit as st
import hmac
import hashlib
import json
from datetime import datetime, timedelta
from database import get_usuario, tornar_assinante
import os

def verificar_assinatura_mercadopago(payload, signature, secret):
    """
    Verifica se a notificação realmente veio do Mercado Pago
    Usa HMAC-SHA256 para segurança
    """
    if not secret:
        return False
    
    expected = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature)

def extrair_email_do_payload(payload):
    """
    Tenta extrair o email do pagador do payload do Mercado Pago
    O formato exato depende do tipo de notificação
    """
    try:
        data = json.loads(payload)
        
        # Diferentes lugares onde o email pode estar
        if 'email' in data:
            return data['email']
        elif 'data' in data and 'email' in data['data']:
            return data['data']['email']
        elif 'payer' in data and 'email' in data['payer']:
            return data['payer']['email']
        elif 'additional_info' in data and 'payer' in data['additional_info'] and 'email' in data['additional_info']['payer']:
            return data['additional_info']['payer']['email']
        
        return None
    except:
        return None

def processar_webhook(payload, signature=None):
    """
    Função principal para processar webhook
    Chamada pelo app.py quando receber POST
    """
    
    # Carrega secret das credenciais
    mercadopago_webhook_secret = None
    
    # Tenta dos secrets do Streamlit
    try:
        mercadopago_webhook_secret = st.secrets.get("MERCADOPAGO_WEBHOOK_SECRET")
    except:
        pass
    
    # Tenta do .env (para desenvolvimento local)
    if not mercadopago_webhook_secret:
        from dotenv import load_dotenv
        load_dotenv()
        mercadopago_webhook_secret = os.getenv("MERCADOPAGO_WEBHOOK_SECRET")
    
    # Se tem signature e secret, verifica autenticidade
    if signature and mercadopago_webhook_secret:
        if not verificar_assinatura_mercadopago(payload, signature, mercadopago_webhook_secret):
            return {"status": "error", "message": "Assinatura inválida"}
    
    # Extrai email do pagador
    email = extrair_email_do_payload(payload)
    
    if not email:
        return {"status": "error", "message": "Email não encontrado no payload"}
    
    # Verifica se usuário existe
    usuario = get_usuario(email)
    
    if not usuario:
        # Se não existe, cria? Melhor não - só existem usuários que fizeram login
        return {"status": "error", "message": "Usuário não encontrado"}
    
    # Libera acesso por 30 dias
    tornar_assinante(email, dias=30)
    
    return {
        "status": "success", 
        "message": f"Assinatura liberada para {email} por 30 dias"
    }