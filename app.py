import streamlit as st

st.set_page_config(
    page_title="Painel Jurídico - Assistente LM",
    page_icon="⚖️",
    layout="wide"
)

# 1. Definimos explicitamente as páginas do nosso SaaS
dashboard = st.Page(
    "app.py", # Ou o arquivo correspondente ao seu painel principal, se movido
    title="Painel Principal",
    icon="📊",
    default=True
)

# Aponta para o seu arquivo existente na pasta pages
assistente_page = st.Page(
    "pages/1_💬_Assistente.py",
    title="Assistente",
    icon="💬"
)

# 2. Criamos a navegação controlada onde nomeamos o grupo como "Painel Jurídico"
pg = st.navigation({
    "⚖️ Painel Jurídico": [
        dashboard,
        assistente_page
    ]
})

# 3. Executamos a navegação
pg.run()
