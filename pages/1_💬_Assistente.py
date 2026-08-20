import os
import tempfile
import streamlit as st
from groq import Groq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader

# Configuração da Página
st.set_page_config(page_title="Assistente Jurídico IA", layout="wide")

st.markdown("""
    <style>
    /* Deixa a barra lateral mais escura e elegante */
    [data-testid="stSidebar"] {
        background-color: #061017 !important;
        border-right: 1px solid #13384A !important;
    }
    
    /* Estilo suave e confortável para os botões */
    div.stButton > button:not(:disabled) {
        border: 1px solid #2B5265 !important;
        color: #E0F7FA !important;
        border-radius: 8px !important;
        background-color: #13384A !important;
        transition: all 0.2s ease !important;
        font-weight: 500 !important;
    }
    
    /* Efeito Hover suave (ao passar o mouse) */
    div.stButton > button:hover:not(:disabled) {
        background-color: #1D4E64 !important;
        border-color: #00F2FE !important;
        color: #FFFFFF !important;
        box-shadow: none !important;
    }
    
    /* Estilização da barra de input do chat mais discreta */
    [data-testid="stChatInput"] {
        max-width: 750px;
        margin: 0 auto;
        border-radius: 10px !important;
        background-color: #13384A !important;
        border: 1px solid #2B5265 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- CSS para aplicar o fundo com gradiente ---
st.markdown(
    """
    <style>
    /* Fundo com gradiente escuro */
    .stApp {
        background: linear-gradient(135deg, #0f0717 0%, #170524 40%, #050505 100%);
        background-attachment: fixed;
    }
    
    /* Sombra forte e bem definida no título principal do Streamlit */
    h1 {
        text-shadow: 0px 4px 12px rgba(0, 0, 0, 0.9), 0px 1px 3px rgba(0, 0, 0, 0.8) !important;
    }
    
    /* Barra lateral escura */
    [data-testid="stSidebar"] {
        background-color: #08040c;
        border-right: 1px solid #170524;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 1. CONTROLE DE LOGIN ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("⚖️ Assistente Jurídico LM AI")
    st.markdown("Faça login para acessar o painel restrito.")
    
    with st.form("login_form"):
        email_input = st.text_input("E-mail de Acesso")
        password_input = st.text_input("Senha", type="password")
        submit_button = st.form_submit_button("Entrar")
        
        if submit_button:
            if email_input == "sergiolmendes2026@gmail.com" and password_input == "123456":
                st.session_state.authenticated = True
                st.session_state.name = "Dr. Sérgio Luiz"
                st.success("Login realizado com sucesso! Carregando...")
                st.rerun()
            else:
                st.error("❌ E-mail ou senha incorretos.")
    
    st.stop()

name = st.session_state.name

# Carregamento seguro da API Key da Groq
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("Erro de configuração: A chave da API Groq não foi encontrada nos segredos.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# Inicializa Histórico de Chat na Sessão
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Diretório da Base de Conhecimento Corporativa ---
PASTA_BASE_CORPORATIVA = "base_conhecimento_corporativa"
os.makedirs(PASTA_BASE_CORPORATIVA, exist_ok=True)

# --- Barra Lateral (Navegação, Perfil e Logout) ---
with st.sidebar:
    st.markdown("⚖️ **Painel Jurídico**")
    st.markdown(f"👤 Olá, **{name}**")
    st.markdown("---")
    
    # Seletor de páginas (Chat vs Base de Conhecimento)
    pagina_selecionada = st.radio(
        "Navegação", 
        ["Assistente Jurídico", "Base de Conhecimento"]
    )
    
    st.markdown("---")
    
    if pagina_selecionada == "Assistente Jurídico":
        st.info("1. Envie seus documentos.\n2. Use as sugestões ou digite.\n3. Analise as respostas com fontes.")
        if st.button("🗑️ Limpar Histórico"):
            st.session_state.messages = []
            st.rerun()
            
    # Botão de Logout simples
    if st.button("🚪 Sair do Sistema"):
        st.session_state.authenticated = False
        st.session_state.messages = []
        st.rerun()

# --- PÁGINA: BASE DE CONHECIMENTO ---
if pagina == "Base de Conhecimento":
    st.markdown("## 📚 Gestão da Base Corporativa")
    arquivos_base = st.file_uploader("Envie documentos", type=["pdf", "docx", "txt"], accept_multiple_files=True)
    
    if arquivos_base and st.button("Indexar na Base"):
        with st.spinner("Processando..."):
            documents = []
            for arq in arquivos_base:
                # Salva arquivo físico
                caminho_fisico = os.path.join(PASTA_BASE_CORPORATIVA, arq.name)
                with open(caminho_fisico, "wb") as f: f.write(arq.getbuffer())
                
                # Carrega o documento
                with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{arq.name}") as tmp:
                    tmp.write(arq.getbuffer()); tmp_path = tmp.name
                
                loader = PyPDFLoader(tmp_path) if arq.name.endswith(".pdf") else (Docx2txtLoader(tmp_path) if arq.name.endswith(".docx") else TextLoader(tmp_path))
                docs = loader.load()
                documents.extend(docs)
                os.unlink(tmp_path)
                st.write(f"📄 Documento '{arq.name}' carregado com {len(docs)} páginas/seções.")

            # Indexação
            splits = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(documents)
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            
            # CRIAÇÃO DO BANCO PERSISTENTE
            st.session_state.vectorstore = Chroma.from_documents(
                documents=splits, 
                embedding=embeddings, 
                persist_directory="chroma_db_corporativo"
            )
            
            st.success(f"✅ Sucesso! {len(splits)} fragmentos de texto indexados.")
                
                # Salva em um banco ChromaDB dedicado à base corporativa (persistido em pasta local)
                persist_directory = "chroma_db_corporativo"
                vectorstore_corporativo = Chroma.from_documents(
                    documents=splits, 
                    embedding=embeddings, 
                    persist_directory=persist_directory
                )
                
                st.success("✅ Documentos indexados com sucesso na Base Corporativa da Empresa!")

    st.markdown("---")
    st.markdown("### 🗂️ Documentos Atuais na Base:")
    
    arquivos_existentes = os.listdir(PASTA_BASE_CORPORATIVA)
    if arquivos_existentes:
        for arq in arquivos_existentes:
            st.text(f"📄 {arq}")
    else:
        st.info("Nenhum documento cadastrado na base corporativa ainda.")

# --- LÓGICA DA PÁGINA: ASSISTENTE JURÍDICO (CHAT) ---
elif pagina_selecionada == "Assistente Jurídico":
    st.title("⚖️ Assistente Jurídico Inteligente")
    st.markdown("Análise avançada de contratos e documentos com segurança de dados.")
    
    # --- Upload de Arquivos para o Chat ---
    uploaded_files = st.file_uploader("📄 Envie documentos (PDF, Word, TXT)", type=["pdf", "docx", "txt"], accept_multiple_files=True)

    if uploaded_files and "vectorstore" not in st.session_state:
        with st.spinner("⚙️ Processando e indexando documentos..."):
            documents = []
            for uploaded_file in uploaded_files:
                with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                if uploaded_file.name.endswith(".pdf"): loader = PyPDFLoader(tmp_path)
                elif uploaded_file.name.endswith(".docx"): loader = Docx2txtLoader(tmp_path)
                else: loader = TextLoader(tmp_path)
                
                documents.extend(loader.load())
                os.unlink(tmp_path)

            splits = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(documents)
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            st.session_state.vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
            st.success("✅ Documentos indexados com sucesso!")
            st.rerun()

    # --- Botões de Sugestão Rápida e Entrada de Chat Unificadas ---
    active_query = None

    if uploaded_files:
        st.markdown("---")
        st.markdown("#### 💡 Sugestões de perguntas rápidas:")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Resumir Contrato"):
                active_query = "Faça um resumo geral dos principais pontos deste contrato."
        with col2:
            if st.button("💰 Valor Total"):
                active_query = "Qual é o valor total do contrato e as condições de pagamento?"
        with col3:
            if st.button("⚠️ Multas e Rescisão"):
                active_query = "Quais são as multas previstas e as regras de rescisão?"

    # Pega também o que o usuário digitar no chat input
    chat_input_query = st.chat_input("Digite sua dúvida jurídica...")
    if chat_input_query:
        active_query = chat_input_query

    # --- Exibição do Histórico do Chat ---
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # --- Execução da IA (Acionada por botão ou chat) ---
    if active_query:
        st.session_state.messages.append({"role": "user", "content": active_query})
        with st.chat_message("user"):
            st.markdown(active_query)
        
        if "vectorstore" in st.session_state and st.session_state.vectorstore is not None:
            with st.chat_message("assistant"):
                with st.spinner("🤔 Analisando documentos com IA..."):
                    retriever = st.session_state.vectorstore.as_retriever(search_kwargs={"k": 3})
                    docs = retriever.invoke(active_query)
                    
                    if not docs:
                        st.warning("⚠️ Não encontrei essa informação nos documentos carregados.")
                    else:
                        context = "\n\n".join([f"[Fonte: {doc.metadata.get('source', 'Documento')}] {doc.page_content}" for doc in docs])
                        
                        prompt_content = f"""Você é um assistente jurídico restrito. Responda à pergunta do usuário **apenas** com base no contexto fornecido abaixo. Se a resposta não estiver no contexto, informe que o documento não contém essa informação. Não utilize conhecimento externo.
                        
Contexto:
{context}

Pergunta: {active_query}
"""
                        
                        chat_completion = client.chat.completions.create(
                            messages=[{"role": "user", "content": prompt_content}],
                            model="openai/gpt-oss-120b",
                            temperature=0.1
                        )
                        
                        response = chat_completion.choices[0].message.content
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            with st.chat_message("assistant"):
                st.error("⚠️ Atenção: Por favor, faça o upload de um documento (PDF, Word ou TXT) antes de realizar consultas.")
