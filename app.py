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

with st.sidebar:
    st.markdown("## ⚖️ Painel Corporativo")
    st.markdown("👤 **Dr. Sérgio Luiz**")
    st.markdown("<span style='color: #10B981; font-size: 14px;'>● Online</span>", unsafe_allow_html=True)
    st.markdown("---")
    
    menu_opcao = st.radio(
        "Navegação do Sistema",
        ["💬 Assistente RAG", "🤖 Assistente de Triagem"]
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

    texto_documentos = ""
    if uploaded_files:
        import pypdf
        for arquivo in uploaded_files:
            try:
                leitor_pdf = pypdf.PdfReader(arquivo)
                for pagina in leitor_pdf.pages:
                    texto_documentos += pagina.extract_text() or ""
            except Exception:
                texto_documentos += str(arquivo.read(), "utf-8", errors="ignore")
        
        st.success(f"✅ {len(uploaded_files)} documento(s) carregado(s) e processados com sucesso!")
    else:
        st.info("💡 Dica: Envie arquivos de contratos ou petições acima para começar a consulta.")

    if "historico_rag" not in st.session_state:
        st.session_state.historico_rag = [
            {"role": "assistant", "content": "Olá! Envie seu documento acima e faça perguntas específicas sobre o conteúdo dele."}
        ]

    for mensagem in st.session_state.historico_rag:
        with st.chat_message(mensagem["role"]):
            st.markdown(mensagem["content"])

    if query := st.chat_input("Digite sua dúvida jurídica sobre os documentos..."):
        if not uploaded_files:
            st.warning("⚠️ Por favor, envie ao menos um documento antes de fazer perguntas.")
        else:
            st.session_state.historico_rag.append({"role": "user", "content": query})
            with st.chat_message("user"):
                st.markdown(query)

            try:
                llm = ChatGroq(
                    temperature=0.2,
                    model_name="openai/gpt-oss-20b",
                    groq_api_key=GROQ_API_KEY
                )

                prompt_rag_sistema = SystemMessage(content=(
                    "Você é um assistente jurídico especialista em análise de contratos e documentos. "
                    "Responda estritamente com base no texto do documento fornecido abaixo. "
                    "Se a resposta não estiver no documento, informe claramente.\n\n"
                    f"--- DOCUMENTO(S) ---\n{texto_documentos[:15000]}"
                ))
                
                mensagens_rag = [prompt_rag_sistema, HumanMessage(content=query)]

                with st.spinner("Analisando o documento com inteligência artificial..."):
                    resposta_ia = llm.invoke(mensagens_rag)

                st.session_state.historico_rag.append({"role": "assistant", "content": resposta_ia.content})
                with st.chat_message("assistant"):
                    st.markdown(resposta_ia.content)

            except Exception as e:
                st.error(f"Erro ao processar a análise com a IA: {e}")

# MÓDULO 2: ASSISTENTE DE TRIAGEM
elif menu_opcao == "🤖 Assistente de Triagem":
    st.title("🤖 Assistente de Triagem Jurídica")
    st.markdown("Atendimento inicial automatizado para identificar a demanda, coletar informações e encaminhar o cliente ao setor responsável.")
    
    with st.expander("ℹ️ Sobre o Fluxo de Atendimento e Conformidade"):
        st.markdown("""
        * **Arquitetura do Fluxo:** `Cliente` ➔ `WhatsApp` ➔ **Assistente de Triagem** ➔ `Identificação da Demanda` ➔ `Perguntas de Triagem` ➔ `Classificação` ➔ `Encaminhamento ao Advogado`.
        * **Aviso Legal:** *Este assistente realiza exclusivamente triagem automatizada e apoio informacional preliminar. A análise técnica, aconselhamento e parecer jurídico definitivo são de responsabilidade exclusiva do advogado titular.*
        """)
    
    st.markdown("---")

    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
    if not GROQ_API_KEY:
        st.error("⚠️ Chave da API do Groq não configurada nos Segredos do Streamlit Cloud.")
        st.stop()

    PROMPT_JURIDICO_WHATSAPP = """
Você é o Assistente Virtual Oficial de um escritório de advocacia, responsável pelo
ATENDIMENTO INICIAL E TRIAGEM JURÍDICA de potenciais clientes.

==================================================
1. IDENTIDADE E OBJETIVO
==================================================

Sua função é realizar o primeiro atendimento de forma profissional, cordial,
clara e humanizada.

Seu objetivo é:
- acolher o potencial cliente;
- compreender o problema apresentado;
- identificar a área jurídica relacionada;
- coletar os fatos essenciais;
- identificar documentos relevantes;
- identificar possíveis prazos ou situações urgentes;
- fazer perguntas de triagem de forma progressiva;
- classificar a demanda;
- organizar as informações coletadas;
- preparar o encaminhamento para um advogado do escritório.

Você NÃO substitui um advogado e NÃO realiza aconselhamento jurídico definitivo.
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
            
            with st.spinner("O bot está processando a triagem..."):
                resposta_ia = llm.invoke(st.session_state.mensagens_bot)
                
            st.session_state.mensagens_bot.append(resposta_ia)
            st.session_state.historico_chat.append({"role": "assistant", "content": resposta_ia.content})
            with st.chat_message("assistant"):
                st.markdown(resposta_ia.content)
                
        except Exception as e:
            st.error(f"Erro ao processar a resposta da IA: {e}")
