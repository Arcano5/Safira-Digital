# app.py - Versão SEM banco de dados
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

# Importar módulos (menos db)
from ia_services import (
    RateLimiter, extrair_texto_arquivo, analisar_formatacao_ats,
    analisar_com_ia
)
from auth_simple import (  # Versão simplificada sem banco
    verificar_callback_google, gerar_url_google, fazer_logout
)
from style import aplicar_estilo

# Configuração
st.set_page_config(
    page_title="Leonor - Análise Anti-ATS", 
    page_icon="🎯",
    layout="wide"
)

# Estilo
cores_site = {
    'primaria': '#0066cc',
    'fundo': '#ffffff',
    'texto': '#333333',
    'fonte': 'Inter, sans-serif'
}
aplicar_estilo(cores_site)

# Carregar segredos
def carregar_segredos():
    caminho_env = Path(__file__).parent / ".env"

    if caminho_env.exists():
        load_dotenv(dotenv_path=caminho_env)
        gemini_key = os.getenv("GEMINI_API_KEY")
        app_url = os.getenv("APP_URL", "http://localhost:8501")
        if gemini_key:
            return {
                "GEMINI_API_KEY": gemini_key,
                "APP_URL": app_url
            }
        
    if hasattr(st, 'secrets') and st.secrets:
        return {
            "GEMINI_API_KEY": st.secrets.get("GEMINI_API_KEY", ""),
            "APP_URL": st.secrets.get("APP_URL", "http://localhost:8501")
        }
    

    # Se não encontrou nada
    st.error("""
    ❌ GEMINI_API_KEY não encontrada!
    
    Para teste local:
    1. Crie um arquivo `.env` na pasta antiAITS/
    2. Adicione: GEMINI_API_KEY=sua_chave_aqui
    
    Para Streamlit Cloud:
    Configure nos Secrets do app
    """)
    st.stop()

config = carregar_segredos()
rate_limiter = RateLimiter(max_calls_per_minute=5)

# Controle de uso local
if 'uso_count' not in st.session_state:
    st.session_state['uso_count'] = 0

# Sidebar
with st.sidebar:
    st.title("🎯 Leonor - Anti-ATS")
    st.caption("Modo demonstração (sem banco de dados)")
    
    st.markdown(
        f"""
        <a href="/" target="_blank" style="
            display: block;
            padding: 0.5rem;
            background-color: transparent;
            color: {cores_site['primaria']};
            border: 2px solid {cores_site['primaria']};
            border-radius: 8px;
            text-align: center;
            text-decoration: none;
            margin-bottom: 1rem;
        ">
            ⬅️ Voltar ao Portal
        </a>
        """,
        unsafe_allow_html=True
    )
    
    st.info(f"👤 Análises: {st.session_state['uso_count']}/10 (modo teste)")
    st.progress(min(st.session_state['uso_count']/10, 1.0))
    
    st.divider()
    st.caption("🔧 Modo simplificado - Banco desativado")

# Conteúdo principal
st.title("🛡️ Leonor - Análise Anti-ATS (Modo Teste)")
st.markdown("Teste gratuito - 10 análises por sessão")
st.divider()

# Formulário
with st.form("form_analise"):
    titulo = st.text_input("Título da Vaga", placeholder="Ex: Desenvolvedor Front End")
    empresa = st.text_input("Empresa", placeholder="Ex: Empresa XPTO")
    descricao = st.text_area("Descrição da Vaga", height=150)
    arquivo = st.file_uploader("Currículo (PDF/DOCX)", type=['pdf', 'docx'])
    
    submit = st.form_submit_button("🚀 Analisar", type="primary", use_container_width=True)

if submit:
    if st.session_state['uso_count'] >= 10:
        st.error("❌ Limite de testes atingido! Recarregue a página para reiniciar.")
        st.stop()
    
    if not all([titulo, empresa, descricao, arquivo]):
        st.error("Preencha todos os campos!")
        st.stop()
    
    with st.spinner("Processando..."):
        # Extrair texto
        texto = extrair_texto_arquivo(arquivo)
        if not texto:
            st.error("Erro ao ler arquivo")
            st.stop()
        
        # Análises
        formatacao = analisar_formatacao_ats(texto)
        resultado = analisar_com_ia(
            descricao, 
            texto, 
            config["GEMINI_API_KEY"],
            rate_limiter
        )
        
        # Incrementar uso
        st.session_state['uso_count'] += 1
        
        # Resultados
        st.success("✅ Análise concluída!")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Match", f"{resultado.get('percentual_match', 0)}%")
        col2.metric("Formatação", f"{formatacao.get('score_formatacao', 0)}%")
        col3.metric("Cargo", resultado.get('cargo_alvo', 'N/A')[:15])
        
        with st.expander("📋 Resultado completo"):
            st.json(resultado)