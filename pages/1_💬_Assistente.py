import os
import tempfile
import streamlit as st
from groq import Groq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
import os
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings

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

# --- 1. CONTROLE DE LOGIN (Apenas a versão limpa e funcional) ---
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
    
    st.stop() # Interrompe a execução até o usuário fazer login

# --- SE O USUÁRIO ESTIVER LOGADO, O SISTEMA SEGUE DAQUI ---

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

# --- Barra Lateral (Perfil e Logout) ---
with st.sidebar:
    st.sidebar.markdown("⚖️ Painel Jurídico")
    st.markdown(f"👤 Olá, **{name}**")
    
    # Botão de Logout simples
    if st.button("🚪 Sair do Sistema"):
        st.session_state.authenticated = False
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("---")
    st.info("1. Envie seus documentos.\n2. Use as sugestões ou digite.\n3. Analise as respostas com fontes.")
    
    if st.button("🗑️ Limpar Histórico"):
        st.session_state.messages = []
        st.rerun()

# --- Interface Principal ---
st.title("⚖️ Assistente Jurídico Inteligente")
st.markdown("Análise avançada de contratos e documentos com segurança de dados.")

# --- Upload de Arquivos ---
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

# --- Botões de Sugestão Rápida ---
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
    
    # Verifica se o banco vetorial existe (ou seja, se um arquivo foi processado)
    if "vectorstore" in st.session_state and st.session_state.vectorstore is not None:
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analisando documentos com IA..."):
                retriever = st.session_state.vectorstore.as_retriever(search_kwargs={"k": 3})
                docs = retriever.invoke(active_query)
                
                # Se não encontrar trechos relevantes no documento
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
                        temperature=0.1 # Temperatura baixa para focar estritamente no texto
                    )
                    
                    response = chat_completion.choices[0].message.content
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        # Se nenhum documento foi enviado, bloqueia e avisa o usuário
        with st.chat_message("assistant"):
            st.error("⚠️ Atenção: Por favor, faça o upload de um documento (PDF, Word ou TXT) antes de realizar consultas.")
