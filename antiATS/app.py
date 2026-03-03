# app.py
import streamlit as st
from datetime import date
from pathlib import Path
from dotenv import load_dotenv
import os

# Importar nossos módulos
from db import (
    inicializar_banco, verificar_limite_uso, incrementar_uso,
    salvar_analise_usuario, salvar_analise_admin, atualizar_newsletter
)
from ia_services import (
    RateLimiter, extrair_texto_arquivo, analisar_formatacao_ats,
    analisar_com_ia
)
from antiATS.auth import (
    verificar_callback_google, gerar_url_google, fazer_logout,
    autenticar_admin
)
# app.py (modificado)
import streamlit as st
from style import aplicar_estilo

# Configuração da página
st.set_page_config(
    page_title="Leonor - Análise Anti-ATS",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# APLICAR ESTILO PERSONALIZADO (depois você substitui pelas cores do React)
cores_site = {
    'primaria': '#0066cc',  # Azul principal
    'fundo': '#ffffff',      # Fundo branco
    'texto': '#333333',      # Texto escuro
    'fonte': 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
}
aplicar_estilo(cores_site)

# Resto do seu código continua igual...

# === CONFIGURAÇÃO INICIAL ===
st.set_page_config(
    page_title="Leonor - Análise Anti-ATS", 
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === CARREGAR SEGREDOS ===
def carregar_segredos():
    caminho_env = Path(__file__).parent / "Segredos.env"
    
    if not caminho_env.exists():
        st.error(f"❌ Arquivo Segredos.env não encontrado")
        st.stop()
    
    load_dotenv(dotenv_path=caminho_env)
    
    return {
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
        "MYSQL_PASSWORD": os.getenv("MYSQL_PASSWORD"),
        "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID"),
        "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET"),
        "ADMIN_PASSWORD": os.getenv("ADMIN_PASSWORD", "leonor2026"),
        "APP_URL": os.getenv("APP_URL", "http://localhost:8501")
    }

config = carregar_segredos()

# === INICIALIZAR COMPONENTES ===
inicializar_banco(config["MYSQL_PASSWORD"])
rate_limiter = RateLimiter(max_calls_per_minute=5)

# === CONTROLE DE USO ANÔNIMO (local) ===
if 'uso_anonimo' not in st.session_state:
    st.session_state['uso_anonimo'] = 0

# === VERIFICAR CALLBACK DO GOOGLE ===
verificar_callback_google(
    config["APP_URL"], 
    config["GOOGLE_CLIENT_ID"], 
    config["GOOGLE_CLIENT_SECRET"],
    config["MYSQL_PASSWORD"]
)

# === SIDEBAR ===
with st.sidebar:
    st.title("🎯 Leonor - Anti-ATS")
    st.caption("Sua aliada contra filtros automáticos")
    
    # Status do usuário
    if st.session_state.get('authenticated'):
        st.success(f"✅ Logado como {st.session_state.get('user_name', 'Usuário')}")
        if st.button("🚪 Sair", key="logout"):
            fazer_logout()
    else:
        st.info("👤 Modo anônimo (3 análises)")
        google_url = gerar_url_google(config["APP_URL"], config["GOOGLE_CLIENT_ID"])
        st.markdown(f'<a href="{google_url}" target="_self"><button style="background-color:#4285F4; color:white; padding:10px; border:none; border-radius:5px; width:100%; cursor:pointer;">🔵 Login com Google</button></a>', unsafe_allow_html=True)
        st.caption("Faça login para salvar histórico e mais análises")
    
    st.divider()
    
    # Contagem de uso
    user_id = st.session_state.get('user_id')
    admin_autenticado = st.session_state.get('admin_autenticado', False)
    
    pode_usar, uso_atual, tipo_usuario, plano = verificar_limite_uso(
        user_id, config["MYSQL_PASSWORD"], admin_autenticado
    )
    
    if tipo_usuario == "anonimo":
        st.progress(st.session_state['uso_anonimo']/3, text=f"Análises: {st.session_state['uso_anonimo']}/3")
        if st.session_state['uso_anonimo'] >= 3:
            st.warning("⚠️ Limite atingido. Faça login para continuar!")
    elif tipo_usuario == "logado":
        if plano == 'free':
            st.progress(uso_atual/3, text=f"Análises do mês: {uso_atual}/3")
        else:
            st.success(f"✨ Plano {plano.capitalize()} - Ilimitado")
    
    st.divider()
    
    # Admin
    is_admin = autenticar_admin(config["ADMIN_PASSWORD"])
    
    st.divider()
    st.info("🤖 **Modelo:** gemini-2.5-flash")
    chamadas, total = rate_limiter.get_status()
    st.caption(f"Chamadas API: {chamadas}/{total}")
    
    st.divider()
    with st.expander("ℹ️ Como usar"):
        st.markdown("""
        1. **Preencha os dados da vaga**
        2. **Faça upload do currículo** (PDF ou DOCX)
        3. **Receba diagnóstico completo**
        
        ✅ Análise privada
        ✅ Plano personalizado
        ✅ Salve seu histórico (login)
        """)

# === CONTEÚDO PRINCIPAL ===
st.title("🛡️ Leonor - Análise Anti-ATS")
st.markdown("Descubra se seu currículo passa nos filtros automáticos")
st.divider()

# Newsletter opt-in para usuários logados
if st.session_state.get('authenticated'):
    with st.container(border=True):
        col_n1, col_n2 = st.columns([3, 1])
        with col_n1:
            newsletter = st.checkbox("📧 Quero receber dicas de carreira por email (você pode cancelar a qualquer momento)")
        with col_n2:
            if st.button("💾 Salvar preferência"):
                atualizar_newsletter(st.session_state['user_id'], newsletter, config["MYSQL_PASSWORD"])
                st.success("Preferência salva!")

# Formulário principal
with st.form("form_analise"):
    st.subheader("📋 Dados da Vaga")
    col1, col2 = st.columns(2)
    with col1:
        titulo = st.text_input("Título da Vaga *", placeholder="Ex: Desenvolvedor Front End")
    with col2:
        empresa = st.text_input("Empresa *", placeholder="Ex: Empresa XPTO")
    
    descricao_vaga = st.text_area(
        "Descrição da Vaga *", 
        height=150,
        placeholder="Cole a descrição completa da vaga..."
    )
    
    st.divider()
    st.subheader("📄 Seu Currículo")
    
    arquivo = st.file_uploader(
        "Upload do currículo (PDF ou DOCX) *",
        type=['pdf', 'docx'],
        help="PDF ou DOCX até 5MB. Seus dados não são armazenados."
    )
    
    st.divider()
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        submit = st.form_submit_button(
            "🚀 Analisar Currículo",
            type="primary",
            use_container_width=True
        )

if submit:
    erros = []
    if not titulo:
        erros.append("❌ Título da vaga obrigatório")
    if not empresa:
        erros.append("❌ Empresa obrigatória")
    if not descricao_vaga:
        erros.append("❌ Descrição da vaga obrigatória")
    if not arquivo:
        erros.append("❌ Currículo obrigatório (PDF ou DOCX)")
    
    if erros:
        for erro in erros:
            st.error(erro)
    else:
        # Verificar limite de uso
        user_id = st.session_state.get('user_id')
        admin_autenticado = st.session_state.get('admin_autenticado', False)
        
        pode_usar, uso_atual, tipo_usuario, plano = verificar_limite_uso(
            user_id, config["MYSQL_PASSWORD"], admin_autenticado
        )
        
        # Ajuste para anônimo
        if tipo_usuario == "anonimo":
            if st.session_state['uso_anonimo'] >= 3:
                st.error("❌ Você atingiu o limite de 3 análises anônimas. Faça login com Google para continuar!")
                google_url = gerar_url_google(config["APP_URL"], config["GOOGLE_CLIENT_ID"])
                st.markdown(f'<a href="{google_url}" target="_self"><button style="background-color:#4285F4; color:white; padding:10px; border:none; border-radius:5px; width:100%; cursor:pointer;">🔵 Login com Google</button></a>', unsafe_allow_html=True)
                st.stop()
        
        if not pode_usar and tipo_usuario != "anonimo":
            st.error("❌ Você atingiu o limite mensal. Assine o plano Premium para análises ilimitadas!")
            st.button("💎 Ver planos", key="ver_planos")
            st.stop()
        
        with st.spinner("📄 Extraindo texto do currículo..."):
            curriculo_texto = extrair_texto_arquivo(arquivo)
            
            if not curriculo_texto:
                st.error("❌ Não foi possível ler o arquivo")
                st.stop()
        
        with st.spinner("🔍 Analisando formatação ATS..."):
            formatacao = analisar_formatacao_ats(curriculo_texto)
        
        with st.spinner("🤖 Leonor está comparando vaga e currículo..."):
            resultado_ia = analisar_com_ia(
                descricao_vaga, 
                curriculo_texto, 
                config["GEMINI_API_KEY"],
                rate_limiter
            )
        
        # Incrementar uso
        if tipo_usuario == "anonimo":
            st.session_state['uso_anonimo'] += 1
        else:
            incrementar_uso(user_id, config["MYSQL_PASSWORD"])
            st.session_state['uso_count'] = st.session_state.get('uso_count', 0) + 1
        
        # Salvar no histórico do usuário (se logado)
        if st.session_state.get('authenticated'):
            salvar_analise_usuario(
                st.session_state['user_id'], 
                titulo, empresa, 
                resultado_ia, 
                config["MYSQL_PASSWORD"]
            )
        
        # Exibir resultados
        st.markdown("---")
        st.subheader("📊 Resultado da Análise")
        
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("📈 Match com a vaga", f"{resultado_ia.get('percentual_match', 0)}%")
        with col_m2:
            st.metric("🔤 Score de Formatação", f"{formatacao.get('score_formatacao', 0)}%")
        with col_m3:
            st.metric("🎯 Cargo Alvo", resultado_ia.get('cargo_alvo', 'N/A')[:20])
        
        st.divider()
        
        col_h1, col_h2 = st.columns(2)
        with col_h1:
            with st.container(border=True):
                st.markdown("### ✅ Hard Skills Encontradas")
                st.write(resultado_ia.get("hard_skills", "N/A"))
        
        with col_h2:
            with st.container(border=True):
                st.markdown("### 🤝 Soft Skills Encontradas")
                st.write(resultado_ia.get("soft_skills", "N/A"))
        
        st.divider()
        
        with st.container(border=True):
            st.markdown("### ❌ Habilidades Faltantes")
            faltantes = resultado_ia.get("habilidades_faltantes", "Não identificado")
            st.error(faltantes)
        
        st.divider()
        
        with st.container(border=True):
            st.markdown("### 📅 Plano de 7 Dias Personalizado")
            plano = resultado_ia.get("plano_7_dias", "")
            linhas = plano.split('\n')
            
            for linha in linhas:
                if linha.strip():
                    st.markdown(f"- {linha.strip()}")
        
        st.divider()
        
        with st.container(border=True):
            st.markdown("### 🔍 Diagnóstico de Formatação ATS")
            
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
            st.info(f"💡 {formatacao.get('dica_rapida', '')}")
        
        st.divider()
        
        with st.container(border=True):
            st.markdown("### 💡 Dica Personalizada")
            st.info(resultado_ia.get("dica_curta", "Continue se desenvolvendo!"))
        
        # Salvar para admin
        if is_admin:
            with st.spinner("💾 Salvando para histórico admin..."):
                salvar_analise_admin(titulo, empresa, resultado_ia, config["MYSQL_PASSWORD"])
                st.success("✅ Análise salva no histórico admin!")
        
        st.divider()
        if st.button("🔄 Nova Análise", use_container_width=True):
            st.rerun()