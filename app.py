import streamlit as st

st.set_page_config(
    page_title="Painel Jurídico - Assistente LM",
    page_icon="⚖️",
    layout="wide"
)

# Define as páginas do sistema de forma limpa
dashboard_page = st.Page(
    "dashboard.py",
    title="Painel Principal",
    icon="📊",
    default=True
)

assistente_page = st.Page(
    "pages/1_💬_Assistente.py",
    title="Assistente",
    icon="💬"
)

# Cria o menu lateral com o nome correto
pg = st.navigation({
    "⚖️ Painel Jurídico": [
        dashboard_page,
        assistente_page
    ]
})

pg.run()
