import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

st.set_page_config(
    page_title="Assistente Jurídico LM AI",
    page_icon="⚖️",
    layout="wide"
)

# Inicializa o estado de autenticação na sessão
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# ==========================================
# 1. TELA DE LOGIN / CADASTRO (SE NÃO LOGADO)
# ==========================================
if not st.session_state.autenticado:
    st.markdown("""
        <style>
        .auth-container {
            max-width: 480px;
            margin: 40px auto;
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

    col_l, col_c, col_r = st.columns([1, 1.4, 1])

    with col_c:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
            <div class="auth-header">
                <h2>⚖️ Assistente Jurídico LM AI</h2>
                <p style="color: #94A3B8; font-size: 14px;">Plataforma inteligente para escritórios de advocacia</p>
            </div>
        """, unsafe_allow_html=True)

        aba_login, aba_cadastro = st.tabs(["🔑 Entrar", "📝 Criar Conta"])

        with aba_login:
            with st.form("form_login_sistema"):
                email_l = st.text_input("E-mail", placeholder="seu.email@escritorio.com", key="l_email")
                senha_l = st.text_input("Senha", type="password", placeholder="••••••••", key="l_senha")
                
                entrar = st.form_submit_button("Acessar Painel", use_container_width=True)
                if entrar:
                    if email_l and senha_l:
                        st.session_state.autenticado = True
                        st.success("Login efetuado com sucesso!")
                        st.rerun()
                    else:
                        st.warning("Preencha todos os campos para entrar.")

        with aba_cadastro:
            with st.form("form_cadastro_sistema"):
                st.markdown("<p style='color: #94A3B8; font-size: 13px;'>Preencha os dados abaixo para solicitar seu registro.</p>", unsafe_allow_html=True)
                
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
                        st.session_state.autenticado = True
                        st.success("Conta criada e sessão iniciada!")
                        st.rerun()
                    elif not termo:
                        st.error("Você precisa aceitar os Termos & Condições.")
                    else:
                        st.warning("Preencha os campos obrigatórios.")
    
    st.stop()

# ==========================================
# 2. SISTEMA INTERNO (APÓS O LOGIN)
# ==========================================

# Barra Lateral Controlada com Segurança
with st.sidebar:
    st.markdown("## ⚖️ Painel Corporativo")
    st.markdown("👤 **Dr. Sérgio Luiz**")
    st.markdown("<span style='color: #10B981; font-size: 14px;'>● Online</span>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Seletor de Módulos (Menu lateral seguro)
    menu_opcao = st.radio(
        "Navegação do Sistema",
        ["💬 Assistente RAG", "🤖 Bot de Triagem"]
    )
    
    st.markdown("---")
    if st.button("🚪 Sair do Sistema", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

# MÓDULO 1: ASSISTENTE RAG
if menu_opcao == "💬 Assistente RAG":
    st.title("💬 Assistente Jurídico Inteligente (RAG)")
    st.markdown("Análise avançada de contratos, petições e documentos com segurança de dados.")
    st.markdown("---")

    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
    if not GROQ_API_KEY:
        st.error("⚠️ Chave da API do Groq não configurada nos Segredos do Streamlit Cloud.")
        st.stop()

    uploaded_files = st.file_uploader(
        "Envie seus documentos jurídicos (PDF, Word, TXT)", 
        type=["pdf", "docx", "txt"], 
        accept_multiple_files=True
    )

    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} documento(s) carregado(s) com sucesso!")
    else:
        st.info("💡 Dica: Envie arquivos de contratos ou petições acima para começar.")

    if query := st.chat_input("Digite sua dúvida jurídica sobre os documentos..."):
        with st.chat_message("user"):
            st.markdown(query)
        with st.chat_message("assistant"):
            with st.spinner("Analisando documentos com IA..."):
                st.markdown(f"Análise preliminar estruturada para: *'{query}'*.")

# MÓDULO 2: BOT DE TRIAGEM
elif menu_opcao == "🤖 Bot de Triagem":
    st.title("🤖 Bot de Atendimento e Triagem Jurídica")
    st.markdown("Simulador do bot de atendimento automatizado para o WhatsApp do escritório.")
    st.markdown("---")

    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
    if not GROQ_API_KEY:
        st.error("⚠️ Chave da API do Groq não configurada nos Segredos do Streamlit Cloud.")
        st.stop()

    PROMPT_JURIDICO_WHATSAPP = """
    Você é o Assistente Virtual Oficial do escritório de advocacia. 
    Sua função é realizar o atendimento inicial, acolhimento e triagem de potenciais clientes.
    """

    if "mensagens_bot" not in st.session_state:
        st.session_state.mensagens_bot = [
            SystemMessage(content=PROMPT_JURIDICO_WHATSAPP),
            HumanMessage(content="Olá! Gostaria de tirar uma dúvida jurídica.")
        ]
        st.session_state.historico_chat = [
            {"role": "assistant", "content": "Olá! Seja bem-vindo(a) ao nosso atendimento jurídico ⚖️. Como posso te ajudar hoje?"}
        ]

    for mensagem in st.session_state.historico_chat:
        with st.chat_message(mensagem["role"]):
            st.markdown(mensagem["content"])

    if user_input := st.chat_input("Digite a mensagem do cliente..."):
        st.session_state.historico_chat.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        try:
            llm = ChatGroq(
                temperature=0.3,
                model_name="openai/gpt-oss-20b",
                groq_api_key=GROQ_API_KEY
            )
            
            st.session_state.mensagens_bot.append(HumanMessage(content=user_input))
            
            with st.spinner("O bot está digitando a resposta..."):
                resposta_ia = llm.invoke(st.session_state.mensagens_bot)
                
            st.session_state.mensagens_bot.append(resposta_ia)
            st.session_state.historico_chat.append({"role": "assistant", "content": resposta_ia.content})
            with st.chat_message("assistant"):
                st.markdown(resposta_ia.content)
                
        except Exception as e:
            st.error(f"Erro ao processar a resposta da IA: {e}")
