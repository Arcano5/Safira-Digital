# app.py - Versão SEM banco de dados
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

# Importar módulos
from ia_services import (
    RateLimiter, extrair_texto_arquivo, analisar_formatacao_ats,
    analisar_com_ia
)
from auth_simple import (
    verificar_callback_google, gerar_url_google, fazer_logout
)
from style import aplicar_estilo

# Configuração da página (DEVE SER O PRIMEIRO COMANDO)
st.set_page_config(
    page_title="Safira Digital - Análise Anti-ATS", 
    page_icon="💎",
    layout="wide"
)

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
    # Tenta .env local primeiro
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
    
    # Tenta secrets do Streamlit Cloud
    if hasattr(st, 'secrets') and st.secrets:
        try:
            return {
                "GEMINI_API_KEY": st.secrets.get("GEMINI_API_KEY", ""),
                "APP_URL": st.secrets.get("APP_URL", "http://localhost:8501")
            }
        except:
            pass
    
    # Se não encontrou nada
    st.error("""
    ❌ **GEMINI_API_KEY não encontrada!**
    
    **Para teste local:**
    1. Crie um arquivo `.env` na pasta antiATS/
    2. Adicione: `GEMINI_API_KEY=sua_chave_aqui`
    
    **Para Streamlit Cloud:**
    Configure nos Secrets do app
    """)
    st.stop()

# Carregar configurações
config = carregar_segredos()
rate_limiter = RateLimiter(max_calls_per_minute=5)

# Controle de uso local
if 'uso_count' not in st.session_state:
    st.session_state['uso_count'] = 0

# ===== SIDEBAR =====
with st.sidebar:
    st.title("💎 Safira Digital")
    st.caption("Análise Anti-ATS")
    
    # Botão de voltar
    st.markdown(
        f"""
        <a href="/" target="_blank" style="
            display: block;
            padding: 0.75rem;
            background-color: transparent;
            color: {cores_site['primaria']};
            border: 2px solid {cores_site['primaria']};
            border-radius: 8px;
            text-align: center;
            text-decoration: none;
            font-weight: 600;
            margin-bottom: 1rem;
            transition: all 0.3s;
        ">
            ⬅️ Voltar ao Portal
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
    
    st.divider()
    
    # Contador de uso
    st.metric("Análises realizadas", f"{st.session_state['uso_count']}/10")
    st.progress(min(st.session_state['uso_count']/10, 1.0))
    
    if st.session_state['uso_count'] >= 10:
        st.warning("⚠️ Limite de testes atingido")
    
    st.divider()
    st.caption("🔧 Modo teste - Banco desativado")

# ===== CONTEÚDO PRINCIPAL =====
st.title("🛡️ Análise Anti-ATS")
st.markdown("Descubra se seu currículo passa nos filtros automáticos")
st.divider()

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
    
    # Botão de submit DENTRO do formulário
    submit = st.form_submit_button(
        "🚀 Analisar Currículo",
        type="primary",
        use_container_width=True
    )

# ===== PROCESSAMENTO (FORA DO FORMULÁRIO) =====
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
        # Verificar limite
        if st.session_state['uso_count'] >= 10:
            st.error("❌ Limite de testes atingido! Recarregue a página para reiniciar.")
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
                    
                    # Incrementar uso
                    st.session_state['uso_count'] += 1
                    
                    # ===== RESULTADOS =====
                    st.success("✅ Análise concluída!")
                    st.divider()
                    
                    # Métricas principais
                    st.subheader("📊 Resultado da Análise")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📈 Match com a vaga", f"{resultado.get('percentual_match', 0)}%")
                    with col2:
                        st.metric("🔤 Score de Formatação", f"{formatacao.get('score_formatacao', 0)}%")
                    with col3:
                        st.metric("🎯 Cargo Alvo", resultado.get('cargo_alvo', 'N/A')[:15])
                    
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
                        faltantes = resultado.get("habilidades_faltantes", "Não identificado")
                        st.error(faltantes)
                    
                    st.divider()
                    
                    # Plano de 7 dias
                    with st.container(border=True):
                        st.markdown("### 📅 Plano de 7 Dias")
                        plano = resultado.get("plano_7_dias", "")
                        for linha in plano.split('\n'):
                            if linha.strip():
                                st.markdown(f"- {linha.strip()}")
                    
                    st.divider()
                    
                    # Diagnóstico de formatação
                    with st.container(border=True):
                        st.markdown("### 🔍 Diagnóstico de Formatação")
                        
                        col_s1, col_s2 = st.columns([1, 2])
                        with col_s1:
                            score = formatacao.get('score_formatacao', 0)
                            if score >= 70:
                                st.success(f"### {score}%")
                            elif score >= 40:
                                st.warning(f"### {score}%")
                            else:
                                st.error(f"### {score}%")
                        
                        with col_s2:
                            problemas = formatacao.get('problemas', [])
                            if problemas:
                                for p in problemas:
                                    st.markdown(p)
                            else:
                                st.success("✅ Nenhum problema grave detectado!")
                    
                    st.divider()
                    
                    # Botão nova análise
                    if st.button("🔄 Nova Análise", use_container_width=True):
                        st.rerun()