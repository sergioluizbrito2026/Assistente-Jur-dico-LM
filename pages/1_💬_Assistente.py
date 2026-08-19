import os
import tempfile
import streamlit as st
from langchain_groq import ChatGroq
from groq import Groq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader, UnstructuredExcelLoader

# Configuração da Página
st.set_page_config(page_title="Assistente Jurídico LM", layout="wide")

# 1. Carregamento seguro da API Key
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("Erro de configuração: A chave da API Groq não foi encontrada nos segredos do sistema.")
    st.stop()

os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# 2. Barra Lateral
with st.sidebar:
    st.header("⚖️ Assistente Jurídico")
    st.markdown("---")
    st.header("Instruções")
    st.markdown("1. Faça o upload dos arquivos.\n2. Processe os dados.\n3. Pergunte.")
    st.warning("Aviso: a IA pode cometer erros. Verifique fatos críticos.")
    st.markdown("---")
    if st.button("📧 Clique Aqui Se Precisar de Suporte"):
        st.write("sergiolmendes2026@gmail.com")

# 3. Inicializa o cliente oficial da Groq
client = Groq(api_key=GROQ_API_KEY)

# 4. Interface de Upload de Arquivos
st.markdown("### Envie documentos (PDF, Word, TXT, Excel)")

uploaded_files = st.file_uploader(
    "Envie seus documentos", 
    type=["pdf", "docx", "txt", "xlsx"], 
    accept_multiple_files=True,
    label_visibility="collapsed"
)

if uploaded_files:
    if "vectorstore" not in st.session_state:
        with st.spinner("Processando e indexando documentos..."):
            documents = []
            for uploaded_file in uploaded_files:
                with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name

                if uploaded_file.name.endswith(".pdf"):
                    loader = PyPDFLoader(tmp_path)
                elif uploaded_file.name.endswith(".docx"):
                    loader = Docx2txtLoader(tmp_path)
                elif uploaded_file.name.endswith(".txt"):
                    loader = TextLoader(tmp_path)
                elif uploaded_file.name.endswith(".xlsx"):
                    loader = UnstructuredExcelLoader(tmp_path)
                else:
                    continue
                
                documents.extend(loader.load())
                os.unlink(tmp_path)

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            splits = text_splitter.split_documents(documents)

            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            st.session_state.vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
            st.success("Documentos processados com sucesso!")

    retriever = st.session_state.vectorstore.as_retriever(search_kwargs={"k": 3})

    # Campo de Chat
    user_query = st.chat_input("Digite sua dúvida jurídica...")
    if user_query:
        with st.chat_message("user"):
            st.write(user_query)
        with st.chat_message("assistant"):
            with st.spinner("Analisando documentos..."):
                # Busca o contexto nos documentos enviados
                relevant_docs = retriever.invoke(user_query)
                context = "\n\n".join(doc.page_content for doc in relevant_docs)

                # Monta a estrutura da pergunta com o contexto
                prompt_content = f"""Responda à pergunta com base apenas no contexto fornecido abaixo. Se não souber a resposta, diga que não sabe.
                
Contexto:
{context}

Pergunta: {user_query}
"""

                # Chamada direta e limpa para a API da Groq
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt_content,
                        }
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0.2,
                )
                
                response = chat_completion.choices[0].message.content
                st.write(response)
else:
    if "vectorstore" in st.session_state:
        del st.session_state.vectorstore
    st.info("Aguardando o upload de documentos para iniciar a análise.")
