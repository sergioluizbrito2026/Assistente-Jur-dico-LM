import os
import tempfile
import streamlit as st
from groq import Groq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader, UnstructuredExcelLoader

st.set_page_config(page_title="Assistente Jurídico Profissional", layout="wide")

# Estilo para diminuir e centralizar a barra de chat inferior
st.markdown("""
    <style>
    [data-testid="stChatInput"] {
        max-width: 750px;
        margin: 0 auto;
    }
    </style>
""", unsafe_allow_html=True)

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

# Upload de Documentos
uploaded_files = st.file_uploader("Envie documentos (PDF, Word, TXT)", type=["pdf", "docx", "txt", "xlsx"], accept_multiple_files=True)

if uploaded_files and "vectorstore" not in st.session_state:
    with st.spinner("Processando e indexando documentos..."):
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
        st.success("Documentos processados com sucesso!")

# Sugestões Rápidas de Perguntas (Aparece se houver documentos indexados)
if "vectorstore" in st.session_state:
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

# Exibição do Histórico do Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada de Texto do Chat
user_query = st.chat_input("Digite sua dúvida...")

# Define qual query processar (se veio do input digitado ou de um botão de sugestão)
query_to_process = user_query
if not user_query and st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    # Se a última mensagem foi adicionada por um botão de sugestão, pega ela para processar
    # Evita duplicar se já foi processada
    pass

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)
    query_to_process = user_query

# Processamento da Resposta da IA com o Histórico e Fontes
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    # Verifica se a última mensagem do usuário ainda não teve resposta do assistente
    # Para evitar loop, processamos o último item caso seja user
    last_msg = st.session_state.messages[-1]["content"]
    
    # Vamos garantir que não processamos duplicado verificando o histórico
    pass

# Lógica limpa de execução do chat
if "vectorstore" in st.session_state:
    # Se a última mensagem enviada foi do usuário, gera a resposta
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        current_prompt = st.session_state.messages[-1]["content"]
        
        # Verifica se o assistente já respondeu a essa exata última mensagem para não duplicar
        # Caso contrário, executa:
        with st.chat_message("assistant"):
            with st.spinner("Analisando documentos..."):
                retriever = st.session_state.vectorstore.as_retriever(search_kwargs={"k": 3})
                docs = retriever.invoke(current_prompt)
                
                context = "\n\n".join([f"[Fonte: {doc.metadata.get('source', 'Contrato')}] {doc.page_content}" for doc in docs])
                
                prompt_content = f"""Responda à pergunta com base no contexto abaixo. Inclua a citação da fonte quando relevante.
                
Contexto:
{context}

Pergunta: {current_prompt}
"""
                
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt_content}],
                    model="openai/gpt-oss-120b",
                    temperature=0.2
                )
                
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
