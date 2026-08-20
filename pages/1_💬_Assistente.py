import os
import tempfile
import streamlit as st
from groq import Groq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader, UnstructuredExcelLoader

st.set_page_config(page_title="Assistente Jurídico Profissional", layout="wide")

# Inicialização da API
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("Erro: API Key não configurada.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# Inicializa Histórico de Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Barra Lateral
with st.sidebar:
    st.header("⚖️ Assistente Jurídico")
    if st.button("Limpar Histórico"):
        st.session_state.messages = []
        st.rerun()

# Upload e Indexação
uploaded_files = st.file_uploader("Envie documentos", type=["pdf", "docx", "txt", "xlsx"], accept_multiple_files=True)

if uploaded_files and "vectorstore" not in st.session_state:
    with st.spinner("Indexando..."):
        documents = []
        for uploaded_file in uploaded_files:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            # Escolha o loader
            if uploaded_file.name.endswith(".pdf"): loader = PyPDFLoader(tmp_path)
            elif uploaded_file.name.endswith(".docx"): loader = Docx2txtLoader(tmp_path)
            else: loader = TextLoader(tmp_path)
            
            documents.extend(loader.load())
            os.unlink(tmp_path)

        splits = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(documents)
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        st.session_state.vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
        st.success("Documentos processados!")

# Exibição do Chat com Histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_query := st.chat_input("Digite sua dúvida..."):
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        retriever = st.session_state.vectorstore.as_retriever(search_kwargs={"k": 3})
        docs = retriever.invoke(user_query)
        
        # Formata contexto com Citação de Fonte
        context = "\n\n".join([f"[Fonte: {doc.metadata.get('source', 'Desconhecida')}] {doc.page_content}" for doc in docs])
        
        prompt_content = f"Responda usando o contexto: \n{context}\n\nPergunta: {user_query}"
        
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt_content}],
            model="openai/gpt-oss-120b",
            temperature=0.2
        )
        
        response = chat_completion.choices[0].message.content
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
