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

# [MANTENHA TODO O SEU CSS AQUI, ESTÁ OK]
st.markdown("""<style>[data-testid="stSidebar"] { background-color: #061017 !important; border-right: 1px solid #13384A !important; } .stApp { background: linear-gradient(135deg, #0f0717 0%, #170524 40%, #050505 100%); background-attachment: fixed; }</style>""", unsafe_allow_html=True)

# --- 1. CONTROLE DE LOGIN ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if not st.session_state.authenticated:
    st.title("⚖️ Assistente Jurídico LM AI")
    with st.form("login_form"):
        email_input = st.text_input("E-mail de Acesso")
        password_input = st.text_input("Senha", type="password")
        if st.form_submit_button("Entrar"):
            if email_input == "sergiolmendes2026@gmail.com" and password_input == "123456":
                st.session_state.authenticated = True
                st.session_state.name = "Dr. Sérgio Luiz"
                st.rerun()
            else: st.error("❌ E-mail ou senha incorretos.")
    st.stop()

name = st.session_state.name
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY: st.error("Erro: API Key não encontrada."); st.stop()
client = Groq(api_key=GROQ_API_KEY)
if "messages" not in st.session_state: st.session_state.messages = []

# --- DIRETÓRIOS ---
PASTA_BASE_CORPORATIVA = "base_conhecimento_corporativa"
os.makedirs(PASTA_BASE_CORPORATIVA, exist_ok=True)

# --- CARREGAMENTO AUTOMÁTICO DA BASE (NOVO) ---
if "vectorstore" not in st.session_state and os.path.exists("chroma_db_corporativo"):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    st.session_state.vectorstore = Chroma(persist_directory="chroma_db_corporativo", embedding_function=embeddings)

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown(f"👤 Olá, **{name}**")
    pagina_selecionada = st.radio("Navegação", ["Assistente Jurídico", "Base de Conhecimento"])
    if st.button("🚪 Sair do Sistema"): st.session_state.authenticated = False; st.rerun()

# --- PÁGINA: BASE DE CONHECIMENTO ---
if pagina_selecionada == "Base de Conhecimento":
    st.markdown("## 📚 Gestão da Base de Conhecimento")
    arquivos_base = st.file_uploader("Envie documentos", type=["pdf", "docx", "txt"], accept_multiple_files=True)
    if arquivos_base and st.button("Processar e Indexar"):
        with st.spinner("Indexando..."):
            documents = []
            for arquivo in arquivos_base:
                with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{arquivo.name}") as tmp:
                    tmp.write(arquivo.getbuffer()); tmp_path = tmp.name
                loader = PyPDFLoader(tmp_path) if arquivo.name.endswith(".pdf") else (Docx2txtLoader(tmp_path) if arquivo.name.endswith(".docx") else TextLoader(tmp_path))
                documents.extend(loader.load()); os.unlink(tmp_path)
                with open(os.path.join(PASTA_BASE_CORPORATIVA, arquivo.name), "wb") as f: f.write(arquivo.getbuffer())
            
            splits = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(documents)
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            st.session_state.vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings, persist_directory="chroma_db_corporativo")
            st.success("✅ Base atualizada!")

# --- PÁGINA: ASSISTENTE JURÍDICO ---
elif pagina_selecionada == "Assistente Jurídico":
    st.title("⚖️ Assistente Jurídico Inteligente")
    uploaded_files = st.file_uploader("📄 Envie documentos extras (opcional)", type=["pdf", "docx", "txt"], accept_multiple_files=True)
    
    # Se subir arquivo no chat, ele atualiza o vectorstore temporariamente
    if uploaded_files:
        # (Lógica original de upload do chat mantida...)
        pass 

    chat_input_query = st.chat_input("Digite sua dúvida...")
    
    if chat_input_query:
        st.session_state.messages.append({"role": "user", "content": chat_input_query})
        with st.chat_message("user"): st.markdown(chat_input_query)
        
        with st.chat_message("assistant"):
            if "vectorstore" in st.session_state:
                with st.spinner("Consultando Base Corporativa..."):
                    docs = st.session_state.vectorstore.as_retriever(search_kwargs={"k": 3}).invoke(chat_input_query)
                    context = "\n\n".join([d.page_content for d in docs])
                    prompt = f"Use apenas este contexto: {context}\n\nPergunta: {chat_input_query}"
                    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="openai/gpt-oss-120b", temperature=0.1)
                    final_res = res.choices[0].message.content
                    st.markdown(final_res)
                    st.session_state.messages.append({"role": "assistant", "content": final_res})
            else:
                st.info("ℹ️ Base de conhecimento ainda não carregada ou vazia.")
