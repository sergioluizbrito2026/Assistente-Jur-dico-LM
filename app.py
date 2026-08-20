import streamlit as st

st.set_page_config(
    page_title="Painel Jurídico - Assistente LM",
    page_icon="⚖️",
    layout="wide"
)

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

pg = st.navigation({
    "⚖️ Painel Jurídico": [
        dashboard_page,
        assistente_page,
        bot_page
    ]
})

pg.run()
