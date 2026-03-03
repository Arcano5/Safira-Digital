# style.py
import streamlit as st

def aplicar_estilo(cores_site):
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        html, body, [class*="css"] {{
            font-family: '{cores_site.get("fonte", "Inter, sans-serif")}';
            color: {cores_site.get("texto", "#333333")};
        }}
        
        .stApp {{
            background-color: {cores_site.get("fundo", "#ffffff")};
        }}
        
        div.stButton > button:first-child {{
            background-color: {cores_site.get("primaria", "#0066cc")};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 500;
        }}
        
        div.stButton > button:first-child:hover {{
            background-color: #004d99;
            border: none;
        }}
        
        h1, h2, h3 {{
            color: {cores_site.get("texto", "#333333")};
            font-weight: 600;
        }}
        
        .stProgress > div > div {{
            background-color: {cores_site.get("primaria", "#0066cc")};
        }}
        
        [data-testid="stMetricValue"] {{
            color: {cores_site.get("primaria", "#0066cc")};
        }}
        
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        </style>
    """, unsafe_allow_html=True)