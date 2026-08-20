import streamlit as st

st.set_page_config(
    page_title="Painel Jurídico AI - Acesso",
    page_icon="⚖️",
    layout="wide"
)

# Estilização CSS refinada para o card de autenticação centralizado
st.markdown("""
    <style>
    .auth-container {
        max-width: 480px;
        margin: 20px auto;
        padding: 30px;
        background: linear-gradient(145deg, #131A26 0%, #0B1017 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.6);
    }
    .auth-header {
        text-align: center;
        margin-bottom: 20px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Centraliza o bloco principal na tela usando colunas
col_l, col_c, col_r = st.columns([1, 1.4, 1])

with col_c:
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="auth-header">
            <h2>⚖️ Assistente Jurídico LM AI</h2>
            <p style="color: #94A3B8; font-size: 14px;">Plataforma inteligente para escritórios de advocacia</p>
        </div>
    """, unsafe_allow_html=True)

    # Abas para alternar entre Login (Sign In) e Cadastro (Sign Up)
    aba_login, aba_cadastro = st.tabs(["🔑 Entrar", "📝 Criar Conta"])

    # ABA 1: LOGIN
    with aba_login:
        with st.form("form_login_sistema"):
            email_l = st.text_input("E-mail", placeholder="seu.email@escritorio.com", key="l_email")
            senha_l = st.text_input("Senha", type="password", placeholder="••••••••", key="l_senha")
            
            entrar = st.form_submit_button("Acessar Painel", use_container_width=True)
            if entrar:
                if email_l and senha_l:
                    st.success("Login efetuado com sucesso!")
                else:
                    st.warning("Preencha todos os campos para entrar.")

    # ABA 2: CADASTRO (SIGN UP)
    with aba_cadastro:
        with st.form("form_cadastro_sistema"):
            st.markdown("<p style='color: #94A3B8; font-size: 13px;'>Preencha os dados abaixo para solicitar seu registro no sistema.</p>", unsafe_allow_html=True)
            
            col_nome, col_sobrenome = st.columns(2)
            with col_nome:
                nome = st.text_input("Nome", placeholder="João")
            with col_sobrenome:
                sobrenome = st.text_input("Sobrenome", placeholder="Silva")
                
            email_c = st.text_input("E-mail Profissional", placeholder="exemplo@user.com", key="c_email")
            senha_c = st.text_input("Senha de Acesso", type="password", placeholder="••••••••", key="c_senha")
            
            termo = st.checkbox("Li e concordo com os Termos & Condições")
            
            cadastrar = st.form_submit_button("Criar Conta", use_container_width=True)
            if cadastrar:
                if nome and email_c and senha_c and termo:
                    st.success("Conta criada com sucesso! Você já pode fazer login.")
                elif not termo:
                    st.error("Você precisa aceitar os Termos & Condições.")
                else:
                    st.warning("Preencha os campos obrigatórios.")
