import streamlit as st

st.set_page_config(
    page_title="Painel Jurídico AI - Enterprise",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS Global Estilo SaaS Executivo
st.markdown("""
    <style>
    /* Fundo geral da aplicação e padrão de fontes */
    .stApp {
        background-color: #0B0E14;
        color: #E2E8F0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Customização da Barra Lateral */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0E131F 0%, #07090D 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    /* Cartões e caixas estilizadas */
    .metric-card {
        background: linear-gradient(135deg, rgba(26, 32, 44, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    
    /* Botões personalizados */
    .stButton>button {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        color: #F8FAFC;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        border-color: #3B82F6;
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# Definição das Páginas do Sistema
dashboard_page = st.Page(
    "dashboard.py",
    title="Painel Principal",
    icon="📊",
    default=True
)

assistente_page = st.Page(
    "pages/1_💬_Assistente.py",
    title="Assistente RAG",
    icon="💬"
)

bot_page = st.Page(
    "pages/2_🤖_Bot_Triagem.py",
    title="Bot de Triagem",
    icon="🤖"
)

# Navegação unificada
pg = st.navigation({
    "⚖️ Módulos Executivos": [
        dashboard_page,
        assistente_page,
        bot_page
    ]
})

pg.run()
