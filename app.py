import streamlit as st

st.set_page_config(
    page_title="Painel Jurídico AI",
    page_icon="⚖️",
    layout="wide"
)

# CSS Customizado para centralizar e compactar a tela de login com elegância
st.markdown("""
    <style>
    /* Centraliza o formulário de login em um card compacto na tela */
    [data-testid="stForm"] {
        max-width: 450px;
        margin: 40px auto;
        padding: 35px;
        background: linear-gradient(145deg, #131A26 0%, #0B1017 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    
    /* Estilização dos inputs para ficarem proporcionais */
    [data-testid="stTextInput"] input {
        background-color: #1A2332;
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 8px;
        color: #F8FAFC;
    }
    
    /* Botão de login com destaque profissional */
    [data-testid="stFormSubmitButton"] button {
        width: 100%;
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 10px;
        transition: all 0.3s ease;
    }
    [data-testid="stFormSubmitButton"] button:hover {
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
        box-shadow: 0 0 15px rgba(37, 99, 235, 0.4);
    }
    </style>
""", unsafe_allow_html=True)
