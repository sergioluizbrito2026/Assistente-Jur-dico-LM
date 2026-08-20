import streamlit as st

# Configuração da página e layout padrão
st.set_page_config(
    page_title="Painel Jurídico AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização visual personalizada para alinhar com o design moderno da barra lateral
st.markdown("""
    <style>
    /* Estilos globais e refinamento da barra lateral */
    section[data-testid="stSidebar"] {
        background-color: #0E1116;
        border-right: 1px solid #1F2937;
    }
    .sidebar-title {
        font-size: 20px;
        font-weight: 700;
        color: #F3F4F6;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Definição das páginas do sistema utilizando o st.Page nativo do Streamlit
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

# Navegação organizada em seções limpas
pg = st.navigation({
    "⚖️ Módulos do Sistema": [
        dashboard_page,
        assistente_page,
        bot_page
    ]
})

# Executa a navegação gerenciada
pg.run()
