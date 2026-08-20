import streamlit as st

st.set_page_config(
    page_title="Painel Jurídico - Assistente LM",
    page_icon="⚖️",
    layout="wide"
)

# --- CSS PARA RENOMEAR O "APP" DA SIDEBAR ---
st.markdown("""
    <style>
    /* Oculta o rótulo padrão 'app' da barra lateral e o substitui por Painel Jurídico */
    [data-testid="stSidebarNav"]::before {
        content: "⚖️ Painel Jurídico";
        display: block;
        margin-left: 20px;
        padding: 10px 0px;
        font-size: 16px;
        font-weight: bold;
        color: #FAFAFA;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚖️ Painel Jurídico AI")
st.markdown("Bem-vindo ao seu painel de controle corporativo.")
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="📄 Documentos Analisados", value="12", delta="+3 hoje")
with col2:
    st.metric(label="💬 Consultas Realizadas", value="48", delta="+12 hoje")
with col3:
    st.metric(label="⚠️ Riscos Identificados", value="5", delta="-2 esta semana")
with col4:
    st.metric(label="💼 Status do Plano", value="Profissional", delta="Ativo")

st.markdown("---")
st.subheader("🚀 Acesso Rápido")

col_a, col_b = st.columns(2)
with col_a:
    st.info("### 💬 Assistente Jurídico (RAG)\nFaça perguntas diretas aos seus contratos e documentos jurídicos.")
    if st.button("Ir para o Assistente ➔"):
        st.switch_page("pages/1_💬_Assistente.py")

with col_b:
    st.success("### 📊 Relatórios e Análises\nAcompanhe o histórico de consultas e relatórios gerados.")
    st.markdown("*Módulo em expansão para a sua conta.*")

st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Assistente Jurídico LM — Todos os direitos reservados © 2026</p>", unsafe_allow_html=True)
