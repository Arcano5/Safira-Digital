# style.py - Identidade Visual Safira Digital
import streamlit as st

def aplicar_estilo(cores_site=None):
    """
    Aplica o tema visual da Safira Digital ao Streamlit
    Se cores_site for fornecido, usa as cores personalizadas
    """
    
    # Cores padrão da Safira Digital
    cores = {
        'primaria': '#0A2472',      # Azul safira escuro
        'secundaria': '#4A6FA5',    # Azul médio
        'destaque': '#FFD700',       # Dourado
        'fundo': '#F5F8FF',          # Azul muito claro
        'texto': '#1E2B3F',          # Azul quase preto
        'cinza': '#6B7280',          # Textos secundários
        'branco': '#FFFFFF',
        'sombra': 'rgba(10, 36, 114, 0.1)'  # Sombra com cor primária
    }
    
    # Se forneceu cores personalizadas, atualiza
    if cores_site:
        cores.update(cores_site)
    
    st.markdown(f"""
        <style>
            /* ===== IMPORTAÇÃO DE FONTES ===== */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
            
            /* ===== RESET E CONFIGURAÇÕES GLOBAIS ===== */
            html, body, [class*="css"] {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                color: {cores['texto']};
            }}
            
            .stApp {{
                background-color: {cores['fundo']};
            }}
            
            /* ===== TÍTULOS ===== */
            h1, h2, h3 {{
                font-weight: 700;
                color: {cores['texto']};
                letter-spacing: -0.02em;
            }}
            
            h1 {{
                font-size: 2.5rem;
                margin-bottom: 0.5rem;
            }}
            
            .stTitle {{
                color: {cores['primaria']};
            }}
            
            /* ===== BOTÕES ===== */
            div.stButton > button:first-child {{
                background: linear-gradient(135deg, {cores['primaria']} 0%, {cores['secundaria']} 100%);
                color: {cores['branco']};
                border: none;
                border-radius: 8px;
                padding: 0.6rem 1.5rem;
                font-weight: 600;
                font-size: 1rem;
                transition: all 0.3s ease;
                box-shadow: 0 4px 6px {cores['sombra']};
                border: 1px solid transparent;
            }}
            
            div.stButton > button:first-child:hover {{
                transform: translateY(-2px);
                box-shadow: 0 10px 15px {cores['sombra']};
                background: linear-gradient(135deg, {cores['secundaria']} 0%, {cores['primaria']} 100%);
                border: 1px solid {cores['destaque']};
            }}
            
            div.stButton > button:first-child:active {{
                transform: translateY(0);
            }}
            
            /* ===== BOTÃO SECUNDÁRIO ===== */
            .stButton > button[kind="secondary"] {{
                background: transparent;
                color: {cores['primaria']};
                border: 2px solid {cores['primaria']};
                box-shadow: none;
            }}
            
            .stButton > button[kind="secondary"]:hover {{
                background: {cores['primaria']};
                color: {cores['branco']};
            }}
            
            /* ===== INPUTS E TEXT AREAS ===== */
            .stTextInput input, .stTextArea textarea {{
                border-radius: 8px;
                border: 2px solid #E5E7EB;
                padding: 0.75rem;
                font-size: 1rem;
                transition: all 0.3s;
                background-color: {cores['branco']};
            }}
            
            .stTextInput input:focus, .stTextArea textarea:focus {{
                border-color: {cores['primaria']};
                box-shadow: 0 0 0 3px {cores['sombra']};
                outline: none;
            }}
            
            /* ===== FILE UPLOADER ===== */
            .stFileUploader {{
                border: 2px dashed {cores['primaria']};
                border-radius: 8px;
                padding: 1rem;
                background-color: {cores['branco']};
                transition: all 0.3s;
            }}
            
            .stFileUploader:hover {{
                border-color: {cores['destaque']};
                background-color: {cores['fundo']};
            }}
            
            /* ===== MÉTRICAS ===== */
            [data-testid="stMetricValue"] {{
                color: {cores['primaria']};
                font-size: 2rem !important;
                font-weight: 800;
            }}
            
            [data-testid="stMetricLabel"] {{
                color: {cores['cinza']};
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
                border: 1px solid #E5E7EB;
                background-color: {cores['branco']};
                padding: 1.5rem;
                box-shadow: 0 4px 6px {cores['sombra']};
                transition: all 0.3s;
            }}
            
            .stContainer:hover {{
                box-shadow: 0 10px 15px {cores['sombra']};
                border-color: {cores['primaria']};
            }}
            
            /* ===== SIDEBAR ===== */
            section[data-testid="stSidebar"] {{
                background-color: {cores['branco']};
                border-right: 1px solid #E5E7EB;
                box-shadow: 2px 0 10px {cores['sombra']};
            }}
            
            section[data-testid="stSidebar"] .stTitle {{
                color: {cores['primaria']};
                font-size: 1.5rem;
                text-align: center;
            }}
            
            /* ===== BOTÃO DE VOLTAR PERSONALIZADO ===== */
            .botao-voltar {{
                display: inline-block;
                width: 100%;
                padding: 0.75rem;
                background-color: transparent;
                color: {cores['primaria']};
                border: 2px solid {cores['primaria']};
                border-radius: 8px;
                text-decoration: none;
                font-weight: 600;
                text-align: center;
                transition: all 0.3s;
                margin-bottom: 1rem;
                font-size: 0.95rem;
            }}
            
            .botao-voltar:hover {{
                background-color: {cores['primaria']};
                color: {cores['branco']};
                transform: translateY(-2px);
                box-shadow: 0 4px 6px {cores['sombra']};
            }}
            
            /* ===== TABS ===== */
            .stTabs [data-baseweb="tab-list"] {{
                gap: 2rem;
                background-color: {cores['branco']};
                padding: 0.5rem;
                border-radius: 8px;
            }}
            
            .stTabs [data-baseweb="tab"] {{
                color: {cores['cinza']};
                font-weight: 500;
                border-radius: 8px;
                padding: 0.5rem 1rem;
                transition: all 0.3s;
            }}
            
            .stTabs [aria-selected="true"] {{
                background-color: {cores['primaria']} !important;
                color: {cores['branco']} !important;
            }}
            
            /* ===== EXPANDERS ===== */
            .streamlit-expanderHeader {{
                background-color: {cores['branco']};
                border-radius: 8px;
                border: 1px solid #E5E7EB;
                transition: all 0.3s;
            }}
            
            .streamlit-expanderHeader:hover {{
                border-color: {cores['primaria']};
                box-shadow: 0 2px 4px {cores['sombra']};
            }}
            
            /* ===== ALERTAS E MENSAGENS ===== */
            .stAlert {{
                border-radius: 8px;
                border-left: 4px solid {cores['primaria']};
                background-color: {cores['branco']};
            }}
            
            .stSuccess {{
                background-color: #10B98120;
                border-left-color: #10B981;
            }}
            
            .stError {{
                background-color: #EF444420;
                border-left-color: #EF4444;
            }}
            
            .stWarning {{
                background-color: #F59E0B20;
                border-left-color: #F59E0B;
            }}
            
            .stInfo {{
                background-color: {cores['primaria']}10;
                border-left-color: {cores['primaria']};
            }}
            
            /* ===== LINKS ===== */
            a {{
                color: {cores['primaria']};
                text-decoration: none;
                font-weight: 500;
                transition: color 0.3s;
            }}
            
            a:hover {{
                color: {cores['destaque']};
                text-decoration: underline;
            }}
            
            /* ===== DIVISORES ===== */
            hr {{
                margin: 2rem 0;
                border: none;
                border-top: 2px solid linear-gradient(90deg, {cores['primaria']}, transparent);
            }}
            
            /* ===== FOOTER ===== */
            footer {{
                visibility: hidden;
            }}
            
            /* ===== ANIMAÇÕES ===== */
            @keyframes fadeIn {{
                from {{
                    opacity: 0;
                    transform: translateY(10px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            
            .stContainer, .stButton, [data-testid="stMetricValue"] {{
                animation: fadeIn 0.5s ease-out;
            }}
            
            /* ===== SCROLLBAR PERSONALIZADA ===== */
            ::-webkit-scrollbar {{
                width: 8px;
                height: 8px;
            }}
            
            ::-webkit-scrollbar-track {{
                background: {cores['fundo']};
            }}
            
            ::-webkit-scrollbar-thumb {{
                background: {cores['primaria']};
                border-radius: 4px;
            }}
            
            ::-webkit-scrollbar-thumb:hover {{
                background: {cores['secundaria']};
            }}
            
        </style>
    """, unsafe_allow_html=True)
    
    # Botão de voltar personalizado (já incluso)
    st.sidebar.markdown(
        f"""
        <a href="/" target="_blank" class="botao-voltar">
            ⬅️ Voltar ao Portal Safira
        </a>
        """,
        unsafe_allow_html=True
    )