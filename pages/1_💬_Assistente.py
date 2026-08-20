import os
import tempfile
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from groq import Groq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader, UnstructuredExcelLoader

# Configuração da Página
st.set_page_config(page_title="Assistente Jurídico SaaS", layout="wide")

# --- Estilização Visual (Azul Petróleo e Destaques Ciano) ---
st.markdown("""
    <style>
    /* Estiliza a barra de input do chat */
    [data-testid="stChatInput"] {
        max-width: 750px;
        margin: 0 auto;
        border-radius: 10px;
        background-color: #13384A !important;
        border: 1px solid #00F2FE !important;
    }
    
    /* Estiliza os botões de sugestão */
    div.stButton > button {
        border: 2px solid #00F2FE;
        color: #00F2FE !important;
        border-radius: 8px;
        background-color: #0A2533;
        transition: all 0.3s ease;
    }
    
    div.stButton > button:hover {
        background-color: #00F2FE;
        color: #0A2533 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 1. CONFIGURAÇÃO DE USUÁRIOS (SaaS Login) ---
# Em produção, você pode puxar isso de um arquivo YAML ou st.secrets. 
# Exemplo de credencial padrão para teste: user "sergio", senha "123456"
# --- 1. CONFIGURAÇÃO DE USUÁRIOS (SaaS Login) ---
credentials = {
    'usernames': {
        'sergio': {
            'name': 'Dr. Sérgio Mendes',
            'password': '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', # Hash para "123456"
            'email': 'sergiolmendes2026@gmail.com'
        }
    }
}

authenticator = stauth.Authenticate(
    credentials,
    cookie_name='assistente_juridico_cookie',
    key='sua_chave_secreta_super_segura',
    cookie_expiry_days=30
)

# Renderiza a tela de login na nova sintaxe
authenticator.login(location='main', key='login_unico')

name = st.session_state.get('name')
authentication_status = st.session_state.get('authentication_status')
username = st.session_state.get('username')

if authentication_status == False:
    st.error('❌ Usuário ou senha incorretos.')
    st.stop()
elif authentication_status == None:
    st.warning('⚠️ Por favor, faça o login para acessar o Assistente Jurídico.')
    st.stop()

# --- SE O USUÁRIO ESTIVER LOGADO, O RESTO DO APP SEGUE DAQUI ---

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
    st.header("⚖️ Painel SaaS")
    st.markdown(f"👤 Olá, **{name}**")
    
    # Botão de Logout oficial do authenticator
    authenticator.logout('🚪 Sair do Sistema', 'sidebar', key='unique_logout')
    
    st.markdown("---")
    st.info("1. Envie seus documentos.\n2. Use as sugestões ou digite.\n3. Analise as respostas com fontes.")
    
    if st.button("🗑️ Limpar Histórico"):
        st.session_state.messages = []
        st.rerun()

# --- Interface Principal ---
st.title("🤖 Assistente Jurídico Inteligente")
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
if uploaded_files:
    st.markdown("---")
    st.markdown("#### 💡 Sugestões de perguntas rápidas:")
    col1, col2, col3 = st.columns(3)
    
    suggested_query = None
    with col1:
        if st.button("📄 Resumir Contrato"):
            suggested_query = "Faça um resumo geral dos principais pontos deste contrato."
    with col2:
        if st.button("💰 Valor Total"):
            suggested_query = "Qual é o valor total do contrato e as condições de pagamento?"
    with col3:
        if st.button("⚠️ Multas e Rescisão"):
            suggested_query = "Quais são as multas previstas e as regras de rescisão?"
            
    if suggested_query:
        st.session_state.messages.append({"role": "user", "content": suggested_query})
        st.rerun()

# --- Exibição do Histórico do Chat ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Entrada de Texto do Chat ---
user_query = st.chat_input("Digite sua dúvida jurídica...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)
    
    if "vectorstore" in st.session_state:
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analisando documentos..."):
                retriever = st.session_state.vectorstore.as_retriever(search_kwargs={"k": 3})
                docs = retriever.invoke(user_query)
                
                context = "\n\n".join([f"[Fonte: {doc.metadata.get('source', 'Documento')}] {doc.page_content}" for doc in docs])
                
                prompt_content = f"""Com base no contexto jurídico abaixo, responda à pergunta do usuário de forma clara e técnica. Cite a fonte do documento.
                
Contexto:
{context}

Pergunta: {user_query}
"""
                
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt_content}],
                    model="openai/gpt-oss-120b",
                    temperature=0.2
                )
                
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        with st.chat_message("assistant"):
            st.write("⚠️ Por favor, faça o upload de um documento primeiro.")
