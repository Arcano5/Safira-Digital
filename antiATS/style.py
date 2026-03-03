# style.py - Identidade Visual Safira Digital
import streamlit as st

def aplicar_estilo(cores_site=None):
    """
    Aplica o tema visual da Safira Digital ao Streamlit
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
        'sombra': 'rgba(10, 36, 114, 0.1)'
    }
    
    if cores_site:
        cores.update(cores_site)
    
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
            
            /* Reset e configurações globais */
            html, body, [class*="css"] {{
                font-family: 'Inter', sans-serif;
                color: {cores['texto']};
            }}
            
            .stApp {{
                background-color: {cores['fundo']};
            }}
            
            /* Títulos */
            h1, h2, h3 {{
                font-weight: 700;
                color: {cores['texto']};
            }}
            
            h1 {{
                font-size: 2.5rem;
                background: linear-gradient(135deg, {cores['primaria']}, {cores['secundaria']});
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            /* Botões */
            div.stButton > button:first-child {{
                background: linear-gradient(135deg, {cores['primaria']} 0%, {cores['secundaria']} 100%);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0.6rem 1.5rem;
                font-weight: 600;
                transition: all 0.3s;
                box-shadow: 0 4px 6px {cores['sombra']};
            }}
            
            div.stButton > button:first-child:hover {{
                transform: translateY(-2px);
                box-shadow: 0 10px 15px {cores['sombra']};
            }}
            
            /* Cards e containers */
            .stContainer {{
                border-radius: 12px;
                border: 1px solid #E5E7EB;
                background-color: {cores['branco']};
                padding: 1.5rem;
                box-shadow: 0 4px 6px {cores['sombra']};
            }}
            
            /* Sidebar */
            section[data-testid="stSidebar"] {{
                background-color: {cores['branco']};
                border-right: 1px solid #E5E7EB;
            }}
            
            /* Botão de voltar */
            .botao-voltar {{
                display: block;
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
            }}
            
            .botao-voltar:hover {{
                background-color: {cores['primaria']};
                color: white;
            }}
            
            /* Mensagens de transparência */
            .stAlert {{
                border-radius: 8px;
                border-left: 4px solid {cores['primaria']};
            }}
            
            /* Animações suaves */
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(10px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            
            .stContainer, .stButton {{
                animation: fadeIn 0.5s ease-out;
            }}
            
            /* Esconder elementos padrão do Streamlit */
            #MainMenu {{visibility: hidden;}}
            footer {{visibility: hidden;}}
            header {{visibility: hidden;}}
            
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