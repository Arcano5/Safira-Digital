# style.py
import streamlit as st

# Adicione no style.py
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def aplicar_estilo(cores_site):
    """
    cores_site: dicionário com as cores do seu site React
    Exemplo: {
        'primaria': '#004a99',
        'fundo': '#f5f5f5',
        'texto': '#333333',
        'fonte': 'Inter, sans-serif'
    }
    """
    
    st.markdown(f"""
        <style>
        /* Fonte global */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        html, body, [class*="css"] {{
            font-family: '{cores_site.get('fonte', 'Inter, sans-serif')}';
            color: {cores_site.get('texto', '#333333')};
        }}
        
        /* Fundo da aplicação */
        .stApp {{
            background-color: {cores_site.get('fundo', '#ffffff')};
        }}
        
        /* Botões primários */
        div.stButton > button:first-child {{
            background-color: {cores_site.get('primaria', '#004a99')};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all 0.3s;
        }}
        
        div.stButton > button:first-child:hover {{
            background-color: {ajustar_cor(cores_site.get('primaria', '#004a99'), 20)};
            border: none;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        
        /* Links */
        a {{
            color: {cores_site.get('primaria', '#004a99')};
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
        
        /* Headers */
        h1, h2, h3 {{
            color: {cores_site.get('texto', '#333333')};
            font-weight: 600;
        }}
        
        /* Caixas de texto e inputs */
        .stTextInput input, .stTextArea textarea {{
            border-radius: 8px;
            border: 1px solid #ddd;
        }}
        
        .stTextInput input:focus, .stTextArea textarea:focus {{
            border-color: {cores_site.get('primaria', '#004a99')};
            box-shadow: 0 0 0 2px {cores_site.get('primaria', '#004a99')}20;
        }}
        
        /* Barras de progresso */
        .stProgress > div > div {{
            background-color: {cores_site.get('primaria', '#004a99')};
        }}
        
        /* Métricas */
        [data-testid="stMetricValue"] {{
            color: {cores_site.get('primaria', '#004a99')};
        }}
        
        /* Botão de voltar personalizado */
        .botao-voltar {{
            display: inline-block;
            padding: 0.5rem 1rem;
            background-color: transparent;
            color: {cores_site.get('primaria', '#004a99')};
            border: 2px solid {cores_site.get('primaria', '#004a99')};
            border-radius: 8px;
            text-decoration: none;
            font-weight: 500;
            margin-bottom: 1rem;
            transition: all 0.3s;
        }}
        
        .botao-voltar:hover {{
            background-color: {cores_site.get('primaria', '#004a99')};
            color: white;
        }}
        </style>
    """, unsafe_allow_html=True)
    
    # Menu de retorno personalizado
    st.sidebar.markdown(
        f"""
        <a href="/" target="_blank" class="botao-voltar">
            ⬅️ Voltar ao Portal
        </a>
        <br><br>
        """,
        unsafe_allow_html=True
    )

def ajustar_cor(cor_hex, percentual):
    """Ajusta tom da cor (escurece se positivo, clareia se negativo)"""
    cor = cor_hex.lstrip('#')
    r, g, b = int(cor[0:2], 16), int(cor[2:4], 16), int(cor[4:6], 16)
    
    r = max(0, min(255, r - percentual))
    g = max(0, min(255, g - percentual))
    b = max(0, min(255, b - percentual))
    
    return f"#{r:02x}{g:02x}{b:02x}"