import streamlit as st

st.set_page_config(
    page_title="Painel Jurídico AI",
    page_icon="⚖️",
    layout="wide"
)

# Estilização refinada para o card de login
st.markdown("""
    <style>
    .login-header {
        text-align: center;
        margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

# Cria colunas para centralizar o formulário, deixando as laterais vazias
col_left, col_center, col_right = st.columns([1, 1.2, 1])

with col_center:
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Cabeçalho estilizado
    st.markdown("""
        <div class="login-header">
            <h2>⚖️ Assistente Jurídico LM AI</h2>
            <p style="color: #94A3B8;">Faça login para acessar o painel restrito.</p>
        </div>
    """, unsafe_allow_html=True)

    # Formulário de Acesso isolado no card central
    with st.form("form_login"):
        email = st.text_input("E-mail de Acesso", placeholder="seu.email@escritorio.com")
        senha = st.text_input("Senha", type="password", placeholder="••••••••")
        
        submitted = st.form_submit_button("Entrar no Sistema", use_container_width=True)
        
        if submitted:
            if email and senha:
                st.success("Login realizado com sucesso!")
            else:
                st.error("Preencha todos os campos.")
