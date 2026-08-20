import os
import tempfile
import streamlit as st
from groq import Groq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader, UnstructuredExcelLoader

st.set_page_config(page_title="Assistente Jurídico Pro", layout="wide")

# --- Estilização CSS para Botões e Barra de Chat ---
st.markdown("""
    <style>
    /* Faz a barra de chat se integrar melhor ao fundo azul petróleo */
    [data-testid="stChatInput"] {
        background-color: #13384A !important; 
        border: 1px solid #00F2FE !important;
    }
    
    /* Garante que o texto dentro do chat input fique legível */
    .stTextInput > div > div > input {
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Inicialização da API ---
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("⚠️ Erro: API Key não configurada nos secrets.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# --- Inicializa Histórico de Chat ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Barra Lateral ---
with st.sidebar:
    st.header("⚖️ Assistente Jurídico")
    st.markdown("---")
    st.info("Instruções: Faça upload do arquivo, aguarde processar e inicie o chat.")
    if st.button("🗑️ Limpar Histórico de Chat"):
        st.session_state.messages = []
        st.rerun()

# --- Interface Principal ---
st.title("🤖 Bem-vindo ao seu Assistente Jurídico")
st.markdown("Analise contratos e documentos com IA.")

# --- Upload de Documentos ---
uploaded_files = st.file_uploader("📄 Envie documentos (PDF, Word, TXT)", type=["pdf", "docx", "txt"], accept_multiple_files=True)

# Processamento
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
        st.success("✅ Documentos processados com sucesso! Você já pode perguntar.")
        st.rerun() # Força o refresh para mostrar os botões de sugestão

# --- Botões de Sugestão Rápidos ---
# Agora eles aparecem se houver arquivos enviados, mesmo que ainda não indexados
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
            
    # Se um botão for clicado, adiciona a pergunta ao histórico e força o rerun
    if suggested_query:
        st.session_state.messages.append({"role": "user", "content": suggested_query})
        st.rerun()

# --- Exibição do Histórico do Chat ---
# Cria um container para o chat para separá-lo visualmente
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- Entrada de Texto do Chat ---
user_query = st.chat_input("Digite sua dúvida jurídica...")

# Lógica de processamento do Chat
if user_query:
    # Adiciona input do usuário ao histórico e exibe
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)
    
    # Gera resposta da IA
    if "vectorstore" in st.session_state:
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analisando documentos..."):
                retriever = st.session_state.vectorstore.as_retriever(search_kwargs={"k": 3})
                docs = retriever.invoke(user_query)
                
                context = "\n\n".join([f"[Fonte: {doc.metadata.get('source', 'Documento')}] {doc.page_content}" for doc in docs])
                
                prompt_content = f"""Com base no contexto jurídico abaixo, responda à pergunta do usuário. Cite a fonte do documento.
                
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
                # Adiciona resposta da IA ao histórico
                st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        # Caso o usuário tente perguntar antes de fazer o upload
        with st.chat_message("assistant"):
            st.write("⚠️ Por favor, envie um documento primeiro para iniciar a análise.")
