# app.py - Versão COM autenticação, banco de dados e LGPD
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
import os
import sys
from datetime import datetime
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(__file__))

# Importar módulos
from ia_services import (
    RateLimiter, extrair_texto_arquivo, analisar_formatacao_ats,
    analisar_com_ia
)
from auth_google import processar_callback, fazer_logout, mostrar_tela_login
from database import get_usuario, pode_usar, registrar_uso
from style import aplicar_estilo

# Configuração da página (DEVE SER O PRIMEIRO COMANDO)
st.set_page_config(
    page_title="Safira Digital - Análise Anti-ATS", 
    page_icon="💎",
    layout="wide"
)

# ===== WEBHOOK DO MERCADO PAGO =====
import json
from webhook import processar_webhook

# Verifica se é uma requisição de webhook
if st.query_params.get("webhook") == "mercadopago":
    
    st.markdown("""
    ## 🔔 Webhook recebido
    
    Processando notificação do Mercado Pago...
    """)
    
    # Pega email da query string para teste
    email_teste = st.query_params.get("email")
    
    if not email_teste:
        st.error("❌ Email não fornecido. Use: ?webhook=mercadopago&email=seu@email.com")
        st.stop()
    
    # Cria payload com o email informado
    payload_exemplo = json.dumps({
        "action": "payment.created",
        "email": email_teste,
        "data": {"id": "123456789"},
        "user_id": "12345"
    })
    
    resultado = processar_webhook(payload_exemplo)
    
    if resultado["status"] == "success":
        st.success(f"✅ {resultado['message']}")
    else:
        st.error(f"❌ {resultado['message']}")
    
    # Para não processar o resto do app
    st.stop()

# ===== CORES DA SAFIRA DIGITAL =====
cores_site = {
    'primaria': '#0A2472',
    'secundaria': '#4A6FA5',
    'destaque': '#FFD700',
    'fundo': '#F5F8FF',
    'texto': '#1E2B3F',
    'cinza': '#6B7280',
    'branco': '#FFFFFF',
    'sombra': 'rgba(10, 36, 114, 0.1)'
}

# Aplicar estilo
aplicar_estilo(cores_site)

# ===== FUNÇÃO PARA CARREGAR SEGREDOS =====
def carregar_segredos():
    """Carrega a chave da Gemini: prioridade st.secrets, fallback .env"""
    
    gemini_key = None
    
    # Tenta secrets do Streamlit Cloud
    if hasattr(st, 'secrets') and st.secrets:
        try:
            gemini_key = st.secrets.get("GEMINI_API_KEY")
        except:
            pass
    
    # Se não achou, tenta .env local
    if not gemini_key:
        from dotenv import load_dotenv
        import os
        load_dotenv()
        gemini_key = os.getenv("GEMINI_API_KEY")
    
    if gemini_key:
        return {"GEMINI_API_KEY": gemini_key}
    
    st.error('❌ GEMINI_API_KEY não encontrada')
    st.stop()

# ===== PROCESSAR CALLBACK DO GOOGLE =====
# Isso precisa ser feito ANTES de qualquer outra coisa
if 'code' in st.query_params:
    if processar_callback():
        st.rerun()

# ===== VERIFICA SE USUÁRIO ESTÁ LOGADO =====
if 'usuario' not in st.session_state:
    mostrar_tela_login()
    st.stop()

# ===== USUÁRIO LOGADO =====
usuario = st.session_state['usuario']
email = usuario['email']
nome = usuario['nome']

# Carregar configurações
config = carregar_segredos()
rate_limiter = RateLimiter(max_calls_per_minute=5)

# ===== VERIFICAR SE PODE USAR =====
pode, mensagem, restantes = pode_usar(email)

# ===== SIDEBAR =====
with st.sidebar:
    st.title("💎 Safira Digital")
    st.caption("Análise Anti-ATS")
    
    # Informações do usuário
    st.markdown(f"""
    <div style="background: #F0F4FF; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
        <p style="margin:0; font-weight:600;">👤 {nome}</p>
        <p style="margin:0; font-size:0.8rem; color:#4A5568;">{email}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Status de uso
    usuario_db = get_usuario(email)
    if usuario_db and usuario_db.get('assinante', False):
        st.success("⭐ **Assinante ativo** - Uso ilimitado")
    else:
        usos_hoje = usuario_db['usos_hoje'] if usuario_db else 0
        st.metric("Análises hoje", f"{usos_hoje}/5")
        st.progress(min(usos_hoje/5, 1.0))
        
        if not pode:
            st.warning("⚠️ Limite diário atingido")
    
    # Botão de logout
    if st.button("🚪 Sair", use_container_width=True):
        fazer_logout()
    
    st.divider()
    
    # Botão de voltar
    st.markdown(
        f"""
        <a href="/" target="_blank" class="botao-voltar">
            ⬅️ Voltar ao Portal Safira
        </a>
        """,
        unsafe_allow_html=True
    )
    
    # Mensagem de desenvolvimento
    st.info(
        "🔄 **Ferramenta em desenvolvimento**\n\n"
        "Estamos testando e melhorando diariamente. "
        "Seu feedback é muito bem-vindo!"
    )

# ===== CONTEÚDO PRINCIPAL =====
st.title("🛡️ Análise Anti-ATS")
st.markdown("Descubra se seu currículo passa nos filtros automáticos")
st.divider()

# ===== VERIFICAÇÃO DE LIMITE =====
if not pode:
    st.error(f"""
    ### ⚠️ {mensagem}
    
    Você usou todas as 5 análises gratuitas de hoje.
    
    **Quer continuar?** Assine o plano ilimitado por apenas **R$ 19,90/mês**.
    """)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('''
        <a href="https://www.mercadopago.com.br/subscriptions/checkout?preapproval_plan_id=SEU_PLANO_AQUI" target="_blank">
            <button style="
                background: linear-gradient(135deg, #0A2472, #4A6FA5);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 1rem 2rem;
                font-size: 1.2rem;
                font-weight: 600;
                width: 100%;
                cursor: pointer;
                margin: 1rem 0;
            ">
                ⭐ ASSINAR AGORA
            </button>
        </a>
        ''', unsafe_allow_html=True)
        
        st.caption("💳 Pagamento seguro via Mercado Pago")
    
    st.stop()

# ===== FORMULÁRIO PRINCIPAL =====
with st.form("form_analise"):
    st.subheader("📋 Dados da Vaga")
    
    col1, col2 = st.columns(2)
    with col1:
        titulo = st.text_input("Título da Vaga *", placeholder="Ex: Desenvolvedor Front End")
    with col2:
        empresa = st.text_input("Empresa *", placeholder="Ex: Empresa XPTO")
    
    descricao = st.text_area(
        "Descrição da Vaga *", 
        height=150,
        placeholder="Cole a descrição completa da vaga..."
    )
    
    st.divider()
    st.subheader("📄 Seu Currículo")
    
    arquivo = st.file_uploader(
        "Upload do currículo (PDF ou DOCX) *",
        type=['pdf', 'docx'],
        help="PDF ou DOCX até 5MB"
    )
    
    st.divider()
    
    # Botão de submit
    submit = st.form_submit_button(
        "🚀 Analisar Currículo",
        type="primary",
        use_container_width=True
    )

# ===== PROCESSAMENTO =====
if submit:
    # Validações
    erros = []
    if not titulo:
        erros.append("❌ Título da vaga obrigatório")
    if not empresa:
        erros.append("❌ Empresa obrigatória")
    if not descricao:
        erros.append("❌ Descrição da vaga obrigatória")
    if not arquivo:
        erros.append("❌ Currículo obrigatório")
    
    if erros:
        for erro in erros:
            st.error(erro)
    else:
        with st.spinner("📄 Processando seu currículo..."):
            texto = extrair_texto_arquivo(arquivo)
            if not texto:
                st.error("❌ Erro ao ler o arquivo. Verifique se é PDF ou DOCX válido.")
            else:
                with st.spinner("🔍 Analisando formatação ATS..."):
                    formatacao = analisar_formatacao_ats(texto)
                
                with st.spinner("🤖 Comparando com a vaga..."):
                    resultado = analisar_com_ia(
                        descricao, 
                        texto, 
                        config["GEMINI_API_KEY"],
                        rate_limiter
                    )
                
                # Registrar uso no banco
                registrar_uso(email)
                
                # Buscar contagem atualizada
                usuario_atualizado = get_usuario(email)
                usos_hoje = usuario_atualizado['usos_hoje'] if usuario_atualizado else 0
                restantes = max(0, 5 - usos_hoje)
                
                # ===== RESULTADOS =====
                st.success("✅ Análise concluída!")
                st.divider()
                
                # Métricas principais
                st.subheader("📊 Resultado da Análise")
                col1, col2, col3 = st.columns(3)
                with col1:
                    match = resultado.get('percentual_match', 0)
                    st.metric("📈 Match com a vaga", f"{match}%")
                with col2:
                    score_format = formatacao.get('score_formatacao', 0)
                    st.metric("🔤 Score de Formatação", f"{score_format}%")
                with col3:
                    st.metric("🎯 Cargo Alvo", resultado.get('cargo_alvo', 'N/A')[:15])
                
                # Extrair contagens para o WhatsApp
                faltantes = resultado.get("habilidades_faltantes", "Não identificado")
                excedentes = resultado.get("excedentes", "Nenhuma")
                
                palavras_faltantes = len([s for s in faltantes.split(',') if s.strip()]) if faltantes != "Não identificado" and faltantes != "Nenhuma" else 0
                palavras_excedentes = len([s for s in excedentes.split(',') if s.strip()]) if excedentes != "Nenhuma" else 0
                
                st.divider()
                
                # Skills
                col_h1, col_h2 = st.columns(2)
                with col_h1:
                    with st.container(border=True):
                        st.markdown("### ✅ Hard Skills")
                        st.write(resultado.get("hard_skills", "Não identificado"))
                
                with col_h2:
                    with st.container(border=True):
                        st.markdown("### 🤝 Soft Skills")
                        st.write(resultado.get("soft_skills", "Não identificado"))
                
                st.divider()
                
                # Habilidades faltantes
                with st.container(border=True):
                    st.markdown("### ❌ Habilidades Faltantes")
                    if faltantes and faltantes != "Não identificado" and faltantes != "Nenhuma":
                        st.error(faltantes)
                    else:
                        st.info("Nenhuma habilidade crítica faltante identificada.")
                
                st.divider()
                
                # Habilidades excedentes (NOVO)
                with st.container(border=True):
                    st.markdown("### 🧹 Habilidades Excedentes")
                    if excedentes and excedentes != "Nenhuma":
                        st.warning(excedentes)
                        st.caption("💡 Considere remover ou resumir essas informações para focar no que a vaga pede.")
                    else:
                        st.success("✅ Nenhum conteúdo claramente irrelevante detectado.")
                
                st.divider()
                
                # Diagnóstico de formatação
                with st.container(border=True):
                    st.markdown("### 🔍 Diagnóstico de Formatação")
                    
                    col_s1, col_s2 = st.columns([1, 2])
                    with col_s1:
                        if score_format >= 70:
                            st.success(f"### {score_format}%")
                        elif score_format >= 40:
                            st.warning(f"### {score_format}%")
                        else:
                            st.error(f"### {score_format}%")
                    
                    with col_s2:
                        problemas = formatacao.get('problemas', [])
                        if problemas:
                            for p in problemas:
                                st.markdown(p)
                        else:
                            st.success("✅ Nenhum problema grave detectado!")
                
                st.divider()
                
                # Call-to-action WhatsApp (substitui o plano de 7 dias)
                with st.container(border=True):
                    st.markdown("### 📲 Quer ajuda profissional?")
                    st.markdown("""
                    Precisa de um plano de estudos personalizado ou ajuda para ajustar seu currículo?
                    
                    **Fale diretamente com um consultor da Safira Digital:**
                    """)
                    
                    # Link do WhatsApp com dados dinâmicos
                    numero = "5511992095721"
                    texto_msg = f"Realizei o teste, tive {match}% de match, {palavras_excedentes} excedentes e {palavras_faltantes} faltantes, {score_format}% de formatação. Preciso de ajuda com o currículo."
                    
                    texto_codificado = quote(texto_msg)
                    link_whatsapp = f"https://wa.me/{numero}?text={texto_codificado}"
                    
                    st.markdown(f'''
                    <a href="{link_whatsapp}" target="_blank">
                        <button style="
                            background: #25D366;
                            color: white;
                            border: none;
                            border-radius: 8px;
                            padding: 1rem 2rem;
                            font-size: 1.2rem;
                            font-weight: 600;
                            width: 100%;
                            cursor: pointer;
                            margin: 0.5rem 0;
                        ">
                            📱 FALAR NO WHATSAPP
                        </button>
                    </a>
                    ''', unsafe_allow_html=True)
                    
                    st.caption("🔍 Seu resultado será enviado automaticamente na mensagem.")
                
                st.divider()
                
                # Botão nova análise
                if st.button("🔄 Nova Análise", use_container_width=True):
                    st.rerun()
