# style.py - Identidade Visual Safira Digital (CORRIGIDO)
import streamlit as st

def aplicar_estilo(cores_site=None):
    """
    Aplica o tema visual da Safira Digital ao Streamlit
    """
    
    # Cores padrão da Safira Digital - AJUSTADAS PARA MELHOR CONTRASTE
    cores = {
        'primaria': '#0A2472',      # Azul safira escuro (mantido)
        'secundaria': '#2A4FA5',     # Azul médio mais escuro
        'destaque': '#FFD700',       # Dourado (mantido)
        'fundo': '#FFFFFF',           # Fundo BRANCO (era muito claro)
        'texto': '#1E2B3F',          # Azul quase preto (mantido)
        'texto_claro': '#4A5568',     # Cinza escuro para textos secundários
        'cinza': '#2D3748',           # Cinza mais escuro
        'branco': '#FFFFFF',
        'sombra': 'rgba(10, 36, 114, 0.15)'
    }
    
    if cores_site:
        cores.update(cores_site)
    
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
            
            /* ===== RESET E CONFIGURAÇÕES GLOBAIS ===== */
            html, body, [class*="css"] {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                color: {cores['texto']} !important;
                background-color: {cores['fundo']};
            }}
            
            .stApp {{
                background-color: {cores['fundo']};
            }}
            
            /* ===== TÍTULOS ===== */
            h1, h2, h3 {{
                color: {cores['primaria']} !important;
                font-weight: 700;
            }}
            
            h1 {{
                font-size: 2.5rem;
                background: linear-gradient(135deg, {cores['primaria']}, {cores['secundaria']});
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 0.5rem;
            }}
            
            .stTitle {{
                color: {cores['primaria']} !important;
            }}
            
            /* ===== TEXTO NORMAL ===== */
            p, li, span, div {{
                color: {cores['texto']} !important;
            }}
            
            .stMarkdown p {{
                color: {cores['texto']} !important;
            }}
            
            /* ===== CAPTIONS E TEXTOS SECUNDÁRIOS ===== */
            .stCaption, .stCaption p {{
                color: {cores['texto_claro']} !important;
            }}
            
            /* ===== BOTÕES ===== */
            div.stButton > button:first-child {{
                background: linear-gradient(135deg, {cores['primaria']} 0%, {cores['secundaria']} 100%);
                color: white !important;
                border: none;
                border-radius: 8px;
                padding: 0.6rem 1.5rem;
                font-weight: 600;
                font-size: 1rem;
                transition: all 0.3s ease;
                box-shadow: 0 4px 6px {cores['sombra']};
            }}
            
            div.stButton > button:first-child:hover {{
                transform: translateY(-2px);
                box-shadow: 0 10px 15px {cores['sombra']};
            }}
            
            /* ===== INPUTS E TEXT AREAS ===== */
            .stTextInput input, .stTextArea textarea {{
                border-radius: 8px;
                border: 2px solid #E2E8F0;
                padding: 0.75rem;
                font-size: 1rem;
                background-color: {cores['branco']};
                color: {cores['texto']} !important;
            }}
            
            .stTextInput input:focus, .stTextArea textarea:focus {{
                border-color: {cores['primaria']};
                box-shadow: 0 0 0 3px rgba(10, 36, 114, 0.2);
                outline: none;
            }}
            
            /* ===== PLACEHOLDERS ===== */
            .stTextInput input::placeholder, .stTextArea textarea::placeholder {{
                color: #A0AEC0 !important;
            }}
            
            /* ===== FILE UPLOADER ===== */
            .stFileUploader {{
                border: 2px dashed {cores['primaria']};
                border-radius: 8px;
                padding: 1rem;
                background-color: {cores['fundo']};
            }}
            
            .stFileUploader:hover {{
                border-color: {cores['destaque']};
                background-color: #F7FAFC;
            }}
            
            /* ===== MÉTRICAS ===== */
            [data-testid="stMetricValue"] {{
                color: {cores['primaria']} !important;
                font-size: 2rem !important;
                font-weight: 800;
            }}
            
            [data-testid="stMetricLabel"] {{
                color: {cores['texto_claro']} !important;
                font-weight: 500;
            }}
            
            /* ===== BARRAS DE PROGRESSO ===== */
            .stProgress > div > div {{
                background: linear-gradient(90deg, {cores['primaria']}, {cores['secundaria']});
                border-radius: 10px;
            }}
            
            /* ===== CARDS E CONTAINERS ===== */
            .stContainer {{
                border-radius: 12px;
                border: 1px solid #E2E8F0;
                background-color: {cores['branco']};
                padding: 1.5rem;
                box-shadow: 0 4px 6px {cores['sombra']};
            }}
            
            /* ===== SIDEBAR ===== */
            section[data-testid="stSidebar"] {{
                background-color: {cores['branco']};
                border-right: 1px solid #E2E8F0;
                box-shadow: 2px 0 10px {cores['sombra']};
            }}
            
            section[data-testid="stSidebar"] .stTitle {{
                color: {cores['primaria']} !important;
            }}
            
            section[data-testid="stSidebar"] p {{
                color: {cores['texto']} !important;
            }}
            
            section[data-testid="stSidebar"] .stCaption {{
                color: {cores['texto_claro']} !important;
            }}
            
            /* ===== BOTÃO DE VOLTAR ===== */
            .botao-voltar {{
                display: block;
                width: 100%;
                padding: 0.75rem;
                background-color: transparent;
                color: {cores['primaria']} !important;
                border: 2px solid {cores['primaria']};
                border-radius: 8px;
                text-align: center;
                text-decoration: none;
                font-weight: 600;
                margin-bottom: 1rem;
                transition: all 0.3s;
            }}
            
            .botao-voltar:hover {{
                background-color: {cores['primaria']};
                color: white !important;
                transform: translateY(-2px);
            }}
            
            /* ===== DIVISORES ===== */
            hr {{
                margin: 2rem 0;
                border: none;
                border-top: 2px solid #E2E8F0;
            }}
            
            /* ===== ALERTAS E MENSAGENS ===== */
            .stAlert {{
                border-radius: 8px;
                border-left: 4px solid {cores['primaria']};
                background-color: {cores['fundo']};
            }}
            
            .stSuccess {{
                background-color: #C6F6D5;
                border-left-color: #38A169;
                color: #22543D !important;
            }}
            
            .stError {{
                background-color: #FED7D7;
                border-left-color: #E53E3E;
                color: #742A2A !important;
            }}
            
            .stWarning {{
                background-color: #FEEBC8;
                border-left-color: #DD6B20;
                color: #744210 !important;
            }}
            
            .stInfo {{
                background-color: #E6F0FF;
                border-left-color: {cores['primaria']};
                color: {cores['texto']} !important;
            }}
            
            /* ===== EXPANDERS ===== */
            .streamlit-expanderHeader {{
                background-color: {cores['branco']};
                border-radius: 8px;
                border: 1px solid #E2E8F0;
                color: {cores['texto']} !important;
            }}
            
            /* ===== LINKS ===== */
            a {{
                color: {cores['primaria']} !important;
                text-decoration: none;
                font-weight: 500;
            }}
            
            a:hover {{
                color: {cores['destaque']} !important;
            }}
            
            /* ===== FOOTER ===== */
            footer {{
                visibility: hidden;
            }}
            
            #MainMenu {{visibility: hidden;}}
            
            /* ===== ANIMAÇÕES ===== */
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(10px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            
            .stContainer, .stButton, [data-testid="stMetricValue"] {{
                animation: fadeIn 0.5s ease-out;
            }}
            
        </style>
    """, unsafe_allow_html=True)
    
    # Botão de voltar
    st.sidebar.markdown(
        f"""
        <a href="/" target="_blank" class="botao-voltar">
            ⬅️ Voltar ao Portal Safira
        </a>
        """,
        unsafe_allow_html=True
    )