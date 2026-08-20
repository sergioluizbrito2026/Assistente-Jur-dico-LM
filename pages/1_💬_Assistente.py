import os
import tempfile
import streamlit as st
from groq import Groq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
import shutil

def limpar_base_dados():
    # Deleta a pasta física de documentos
    if os.path.exists(PASTA_BASE_CORPORATIVA):
        shutil.rmtree(PASTA_BASE_CORPORATIVA)
        os.makedirs(PASTA_BASE_CORPORATIVA)
    # Deleta o banco de dados vetorial
    if os.path.exists("chroma_db_corporativo"):
        shutil.rmtree("chroma_db_corporativo")
    # Limpa estado da sessão
    st.session_state.vectorstore = None
    st.rerun()

# Configuração da Página
st.set_page_config(page_title="Assistente Jurídico IA - SaaS", layout="wide")

# Estilo Visual CSS
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #061017 !important; border-right: 1px solid #13384A !important; }
    .stApp { background: linear-gradient(135deg, #0f0717 0%, #170524 40%, #050505 100%); background-attachment: fixed; }
    .stChatMessage { border-radius: 8px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 1. AUTENTICAÇÃO E SESSÃO
# -----------------------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("⚖️ Assistente Jurídico LM AI")
    with st.form("login_form"):
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        if st.form_submit_button("Entrar"):
            if email == "sergiolmendes2026@gmail.com" and senha == "123456":
                st.session_state.authenticated = True
                st.session_state.name = "Dr. Sérgio Luiz"
                st.rerun()
            else:
                st.error("❌ E-mail ou senha incorretos.")
    st.stop()

# Configuração da API do Groq
GROQ_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
if not GROQ_KEY:
    st.error("🔑 Chave da API GROQ não configurada.")
    st.stop()

client = Groq(api_key=GROQ_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = []

PASTA_BASE_CORPORATIVA = "base_conhecimento_corporativa"
os.makedirs(PASTA_BASE_CORPORATIVA, exist_ok=True)

# -----------------------------------------------------------------------------
# 2. CARREGAMENTO DO BANCO DE DADOS VETORIAL (CHROMADB)
# -----------------------------------------------------------------------------
@st.cache_resource
def get_embeddings():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

embeddings = get_embeddings()

def carregar_vectorstore():
    if os.path.exists("chroma_db_corporativo"):
        return Chroma(persist_directory="chroma_db_corporativo", embedding_function=embeddings)
    return None

st.session_state.vectorstore = carregar_vectorstore()

# -----------------------------------------------------------------------------
# 3. BARRA LATERAL (NAVEGAÇÃO E METADADOS)
# -----------------------------------------------------------------------------
# --- BARRA LATERAL (VERSÃO LIMPA E SEM DUPLICAÇÕES) ---
with st.sidebar:
    # Apenas o essencial, sem duplicar o "app"
    st.markdown("💬 **Assistente**")
    st.markdown("---")
    st.markdown("⚖️ **Painel Jurídico**")
    st.markdown(f"👤 Olá, **{st.session_state.name}**")
    
    st.markdown("---")
    st.markdown("### Navegação")
    # Este é o rádio que controla a página
    pagina = st.radio("Selecione a página:", ["Assistente Jurídico", "Base de Conhecimento"], label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("### 📁 Documentos na Base:")
    arquivos_existentes = [f for f in os.listdir(PASTA_BASE_CORPORATIVA) if not f.startswith(".")]
    if arquivos_existentes:
        for arq in arquivos_existentes:
            st.caption(f"• {arq}")
    else:
        st.caption("Nenhum documento na base.")
        
    st.markdown("---")
    if st.button("🚪 Sair do Sistema"): 
        st.session_state.authenticated = False
        st.rerun()

# -----------------------------------------------------------------------------
# 4. PÁGINA: BASE DE CONHECIMENTO (INDEXAÇÃO COM METADADOS)
# -----------------------------------------------------------------------------
if pagina == "Base de Conhecimento":
    st.markdown("## 📚 Gestão da Base de Conhecimento Corporativa")
    st.info("Envie minutas padrão, contratos ou teses para consulta permanente do assistente.")
    
    arquivos_base = st.file_uploader(
        "Envie documentos (PDF, DOCX, TXT)", 
        type=["pdf", "docx", "txt"], 
        accept_multiple_files=True
    )
    
    if arquivos_base and st.button("Indexar na Base de Conhecimento"):
        with st.spinner("Lendo e indexando documentos..."):
            documents = []
            for arq in arquivos_base:
                # Salvar arquivo físico
                caminho_fisico = os.path.join(PASTA_BASE_CORPORATIVA, arq.name)
                with open(caminho_fisico, "wb") as f:
                    f.write(arq.getbuffer())
                
                # Leitura temporária
                with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{arq.name}") as tmp:
                    tmp.write(arq.getbuffer())
                    tmp_path = tmp.name

                if arq.name.endswith(".pdf"):
                    loader = PyPDFLoader(tmp_path)
                elif arq.name.endswith(".docx"):
                    loader = Docx2txtLoader(tmp_path)
                else:
                    loader = TextLoader(tmp_path, encoding="utf-8")

                docs_carregados = loader.load()
                
                # Adiciona o nome do arquivo nos metadados de cada página/trecho
                for doc in docs_carregados:
                    doc.metadata["source"] = arq.name
                    doc.metadata["file_name"] = arq.name
                
                documents.extend(docs_carregados)
                os.unlink(tmp_path)

            if not documents:
                st.warning("⚠️ Nenhum texto pôde ser extraído dos arquivos.")
            else:
                # Divisão em blocos de texto (chunks) com sobreposição
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
                splits = text_splitter.split_documents(documents)

                # Persistência no ChromaDB
                vectorstore = Chroma.from_documents(
                    documents=splits,
                    embedding=embeddings,
                    persist_directory="chroma_db_corporativo"
                )
                st.session_state.vectorstore = vectorstore
                st.success(f"✅ Sucesso! {len(splits)} blocos de texto indexados de {len(arquivos_base)} arquivo(s).")
                st.rerun()

# -----------------------------------------------------------------------------
# 5. PÁGINA: ASSISTENTE JURÍDICO (CHAT COM FILTRO POR DOCUMENTO)
# -----------------------------------------------------------------------------
elif pagina == "Assistente Jurídico":
    st.title("⚖️ Assistente Jurídico Inteligente")

    # Filtro de Seleção de Documento no Chat
    doc_selecionado = "Todos os Documentos"
    if arquivos_existentes:
        doc_selecionado = st.selectbox(
            "🎯 Selecione o documento para consulta (ou consulte toda a base):",
            ["Todos os Documentos"] + arquivos_existentes
        )

    # Exibição do histórico de mensagens
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    query = st.chat_input("Digite sua dúvida sobre os documentos...")

    if query:
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            if st.session_state.vectorstore is None:
                st.warning("⚠️ A base de conhecimento está vazia. Cadastre documentos na aba 'Base de Conhecimento'.")
            else:
                with st.spinner("Consultando a base de conhecimento..."):
                    # Aplicar Filtro de Busca por Metadados
                    search_kwargs = {"k": 6}
                    if doc_selecionado != "Todos os Documentos":
                        search_kwargs["filter"] = {"source": doc_selecionado}

                    retriever = st.session_state.vectorstore.as_retriever(search_kwargs=search_kwargs)
                    docs_encontrados = retriever.invoke(query)

                    if not docs_encontrados:
                        resposta = f"Não foi possível localizar trechos relevantes no documento `{doc_selecionado}` para responder à sua dúvida."
                        st.markdown(resposta)
                    else:
                        # Montar contexto com indicação explícita da fonte
                        contexto = "\n\n---\n\n".join([
                            f"[Fonte: {d.metadata.get('source', 'Desconhecido')}]\n{d.page_content}"
                            for d in docs_encontrados
                        ])

                        prompt = f"""Você é um assistente jurídico especializado em análise contratual e documental.
Responda à dúvida do usuário com base EXCLUSIVAMENTE nos trechos fornecidos abaixo.

Se a informação solicitada (como a qualificação das partes, contratante, contratada, objeto, prazos ou foro) estiver presente no texto, extraia-a e apresente de forma objetiva.
Se os trechos não contiverem a resposta, informe claramente que o trecho recuperado não possui essa informação específica.

TRECHOS DO DOCUMENTO:
{contexto}

PERGUNTA DO USUÁRIO:
{query}
"""

                        res = client.chat.completions.create(
                            messages=[{"role": "user", "content": prompt}],
                            model="openai/gpt-oss-120b",
                            temperature=0.1
                        )
                        resposta = res.choices[0].message.content
                        st.markdown(resposta)

                        # Exibir Painel Expansível de Fontes Consultadas
                        with st.expander("🔍 Ver trechos originais consultados no documento"):
                            for i, d in enumerate(docs_encontrados, 1):
                                fonte = d.metadata.get("source", "N/A")
                                st.markdown(f"**Bloco {i} (Arquivo: {fonte}):**")
                                st.caption(d.page_content)

                    st.session_state.messages.append({"role": "assistant", "content": resposta})
