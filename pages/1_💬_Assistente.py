import os
import tempfile
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader, UnstructuredExcelLoader

# Configuração da Página
st.set_page_config(page_title="Assistente Jurídico LM", layout="wide")

# 1. Carregamento seguro da API Key (Streamlit Secrets ou Variável de Ambiente)
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# 2. Validação se a chave existe no servidor
if not GROQ_API_KEY:
    st.error("Erro de configuração: A chave da API Groq não foi encontrada nos segredos do sistema.")
    st.stop()

# Configura a chave no ambiente para o LangChain/Groq utilizarem
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# 3. Barra Lateral (Modo SaaS - sem pedir chave ao usuário)
with st.sidebar:
    st.header("⚖️ Assistente Jurídico")
    st.markdown("---")
    st.header("Instruções")
    st.markdown("1. Faça o upload dos arquivos.\n2. Processe os dados.\n3. Pergunte.")
    st.warning("Aviso: a IA pode cometer erros. Verifique fatos críticos.")
    
    st.markdown("---")
    if st.button("📧 Clique Aqui Se Precisar de Suporte"):
        st.write("sergiolmendes2026@gmail.com")

# 4. Inicializa o modelo de IA de forma segura
llm = ChatGroq(groq_api_key=GROQ_API_KEY, model="llama-3.1-8b-instant", temperature=0.2)
# 5. Interface de Upload de Arquivos
st.markdown("Envie documentos (PDF, Word, TXT, Excel)")

uploaded_files = st.file_uploader(
    "Envie seus documentos", 
    type=["pdf", "docx", "txt", "xlsx"], 
    accept_multiple_files=True,
    label_visibility="collapsed"
)

if uploaded_files:
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
        vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

        # Prompt e Cadeia RAG
        template = """Responda à pergunta com base apenas no contexto fornecido abaixo. Se não souber a resposta, diga que não sabe.
        
        Contexto:
        {context}
        
        Pergunta: {question}
        """
        prompt = ChatPromptTemplate.from_template(template)

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        st.success("Documentos processados com sucesso! Faça sua pergunta abaixo.")

        # Campo de Chat
        user_query = st.chat_input("Digite sua dúvida jurídica...")
        if user_query:
            with st.chat_message("user"):
                st.write(user_query)
            with st.chat_message("assistant"):
                with st.spinner("Analisando documentos..."):
                    response = rag_chain.invoke(user_query)
                    st.write(response)
else:
    st.info("Aguardando o upload de documentos para iniciar a análise.")
