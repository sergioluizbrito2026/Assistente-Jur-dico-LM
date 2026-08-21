import streamlit as st
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq
import pypdf
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="Assistente Jurídico LM",
    page_icon="⚖️",
    layout="wide"
)

# ==========================================
# 1. ESTADOS DA SESSÃO
# ==========================================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# ==========================================
# TELA DE AUTENTICAÇÃO (LOGIN)
# ==========================================
if not st.session_state.autenticado:
    st.title("⚖️ Assistente Jurídico LM - Acesso Corporativo")
    
    aba_login, aba_cadastro, aba_recuperar = st.tabs(["Entrar", "Criar Conta", "Esqueci a Senha"])
    
    with aba_login:
        st.subheader("Faça seu login")
        email_login = st.text_input("E-mail corporativo", key="login_email")
        senha_login = st.text_input("Senha", type="password", key="login_senha")
        
        if st.button("Entrar no Sistema", use_container_width=True):
            if email_login and senha_login:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.warning("Preencha todos os campos para continuar.")
                
    with aba_cadastro:
        st.subheader("Cadastrar Novo Usuário")
        st.text_input("Nome Completo", key="cad_nome")
        st.text_input("E-mail Corporativo", key="cad_email")
        st.text_input("Senha", type="password", key="cad_senha")
        if st.button("Cadastrar", use_container_width=True):
            st.success("Conta criada com sucesso! Vá para a aba 'Entrar'.")
            
    with aba_recuperar:
        st.subheader("Recuperação de Senha")
        st.text_input("Informe seu e-mail cadastrado", key="rec_email")
        if st.button("Enviar Instruções", use_container_width=True):
            st.info("Se o e-mail constar na base, as instruções foram enviadas.")
            
    st.stop()

# ==========================================
# 2. SISTEMA INTERNO (BARRA LATERAL UNIFICADA)
# ==========================================
with st.sidebar:
    st.markdown("## ⚖️ Painel Corporativo")
    st.markdown("👤 **Dr. Sérgio Luiz**")
    st.markdown("<span style='color: #10B981; font-size: 14px;'>● Online</span>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Menu unificado para evitar conflito de estados
    pagina_selecionada = st.radio(
        "Navegação",
        [
            "🔵 Dashboard", 
            "💬 Assistente Jurídico RAG", 
            "🤖 Triagem Jurídica", 
            "👤 Meu Perfil", 
            "⚙️ Configurações", 
            "🔔 Notificações", 
            "🚪 Sair do Sistema"
        ],
        label_visibility="collapsed"
    )
    
    if pagina_selecionada == "🚪 Sair do Sistema":
        st.session_state.autenticado = False
        st.rerun()

# ==========================================
# 3. ROTEAMENTO DAS TELAS
# ==========================================

if pagina_selecionada == "👤 Meu Perfil":
    st.title("👤 Meu Perfil")
    st.markdown("Gerencie suas informações profissionais.")
    st.markdown("---")
    st.text_input("Nome Completo", value="Dr. Sérgio Luiz")
    st.text_input("E-mail", value="sergio.luiz@escritorio.com")

elif pagina_selecionada == "⚙️ Configurações":
    st.title("⚙️ Configurações")
    st.markdown("Ajustes gerais do sistema.")
    st.markdown("---")
    st.toggle("Modo Escuro", value=True)

elif pagina_selecionada == "🔔 Notificações":
    st.title("🔔 Notificações")
    st.markdown("Avisos recentes.")
    st.markdown("---")
    st.info("Nenhuma nova notificação pendente.")

# MÓDULO: DASHBOARD
elif pagina_selecionada == "🔵 Dashboard":
    st.title("📊 Painel de Controle")
    st.markdown("Bem-vindo ao seu resumo executivo do escritório.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Triagens Realizadas", "24", "+3 desde ontem")
    col2.metric("Documentos RAG", "12", "Estável")
    col3.metric("Urgências Detectadas", "2", "⚠️ Atenção", delta_color="inverse")
    
    st.markdown("---")
    
    st.subheader("📈 Distribuição de Demandas")
    df = pd.DataFrame({'Área': ['Trabalhista', 'Cível', 'Consumidor'], 'Casos': [10, 8, 6]})
    st.bar_chart(df.set_index('Área'))

# MÓDULO: ASSISTENTE JURÍDICO RAG
elif pagina_selecionada == "💬 Assistente Jurídico RAG":
    st.title("💬 Assistente Jurídico Inteligente (RAG)")
    st.markdown("Análise avançada de contratos, petições e documentos com segurança de dados.")
    
    col_t1, col_t2 = st.columns([6, 1])
    with col_t2:
        if st.button("🗑️ Limpar Histórico", use_container_width=True):
            st.session_state.historico_rag = [
                {"role": "assistant", "content": "Olá! Envie seu documento acima e faça perguntas específicas sobre o conteúdo dele."}
            ]
            st.rerun()
            
    st.markdown("---")

    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
    if not GROQ_API_KEY:
        st.error("⚠️ Chave da API do Groq não configurada nos Segredos do Streamlit Cloud.")
        st.stop()

    uploaded_files = st.file_uploader(
        "Envie seus documentos jurídicos (PDF, Word, TXT)", 
        type=["pdf", "docx", "txt"], 
        accept_multiple_files=True
    )

    texto_documentos = ""
    if uploaded_files:
        for arquivo in uploaded_files:
            try:
                leitor_pdf = pypdf.PdfReader(arquivo)
                for pagina in leitor_pdf.pages:
                    texto_documentos += pagina.extract_text() or ""
            except Exception:
                texto_documentos += str(arquivo.read(), "utf-8", errors="ignore")
        
        st.success(f"✅ {len(uploaded_files)} documento(s) carregado(s) e processados com sucesso!")
    else:
        st.info("💡 Dica: Envie arquivos de contratos ou petições acima para começar a consulta.")

    if "historico_rag" not in st.session_state:
        st.session_state.historico_rag = [
            {"role": "assistant", "content": "Olá! Envie seu documento acima e faça perguntas específicas sobre o conteúdo dele."}
        ]

    for mensagem in st.session_state.historico_rag:
        with st.chat_message(mensagem["role"]):
            st.markdown(mensagem["content"])

    if query := st.chat_input("Digite sua dúvida jurídica sobre os documentos..."):
        if not uploaded_files:
            st.warning("⚠️ Por favor, envie ao menos um documento antes de fazer perguntas.")
        else:
            st.session_state.historico_rag.append({"role": "user", "content": query})
            with st.chat_message("user"):
                st.markdown(query)

            try:
                llm = ChatGroq(
                    temperature=0.2,
                    model_name="openai/gpt-oss-20b",
                    groq_api_key=GROQ_API_KEY
                )

                prompt_rag_sistema = SystemMessage(content=(
                    "Você é um assistente jurídico especialista em análise de contratos e documentos. "
                    "Responda estritamente com base no texto do documento fornecido abaixo. "
                    "Se a resposta não estiver no documento, informe claramente.\n\n"
                    f"--- DOCUMENTO(S) ---\n{texto_documentos[:15000]}"
                ))
                
                mensagens_rag = [prompt_rag_sistema, HumanMessage(content=query)]

                with st.spinner("Analisando o documento com inteligência artificial..."):
                    resposta_ia = llm.invoke(mensagens_rag)

                st.session_state.historico_rag.append({"role": "assistant", "content": resposta_ia.content})
                with st.chat_message("assistant"):
                    st.markdown(resposta_ia.content)

            except Exception as e:
                st.error(f"Erro ao processar a análise com a IA: {e}")

# MÓDULO: TRIAGEM JURÍDICA
elif pagina_selecionada == "🤖 Triagem Jurídica":
    st.title("🤖 Triagem Jurídica")
    st.markdown("Atendimento inicial automatizado para identificar a demanda, coletar informações e encaminhar o cliente ao setor responsável.")
    
    col_t1, col_t2 = st.columns([6, 1])
    with col_t2:
        if st.button("🗑️ Limpar Histórico", use_container_width=True, key="limpar_triagem"):
            st.session_state.mensagens_bot = [
                SystemMessage(content="Você é o Assistente Virtual Oficial de um escritório de advocacia, responsável pelo atendimento inicial e triagem jurídica."),
                HumanMessage(content="Olá! Gostaria de tirar uma dúvida jurídica.")
            ]
            st.session_state.historico_chat = [
                {"role": "assistant", "content": "Olá! Seja bem-vindo(a) ao nosso atendimento jurídico ⚖️. Como posso te ajudar hoje?"}
            ]
            st.rerun()

    with st.expander("ℹ️ Sobre o Fluxo de Atendimento e Conformidade"):
        st.markdown("""
        * **Arquitetura do Fluxo:** `Cliente` ➔ `WhatsApp` ➔ **Triagem Jurídica** ➔ `Identificação da Demanda` ➔ `Perguntas de Triagem` ➔ `Classificação` ➔ `Encaminhamento ao Advogado`.
        * **Aviso Legal:** *Este assistente realiza exclusivamente triagem automatizada e apoio informacional preliminar. A análise técnica, aconselhamento e parecer jurídico definitivo são de responsabilidade exclusiva do advogado titular.*
        """)
    
    st.markdown("---")

    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
    if not GROQ_API_KEY:
        st.error("⚠️ Chave da API do Groq não configurada nos Segredos do Streamlit Cloud.")
        st.stop()

    PROMPT_JURIDICO_WHATSAPP = """Você é o Assistente Virtual Oficial de um escritório de advocacia, responsável pelo
ATENDIMENTO INICIAL E TRIAGEM JURÍDICA de potenciais clientes.

==================================================
1. IDENTIDADE E OBJETIVO
==================================================

Sua função é realizar o primeiro atendimento de forma profissional, cordial,
clara e humanizada.

Seu objetivo é:
- acolher o potencial cliente;
- compreender o problema apresentado;
- identificar a área jurídica relacionada;
- coletar os fatos essenciais;
- identificar documentos relevantes;
- identificar possíveis prazos ou situações urgentes;
- fazer perguntas de triagem de forma progressiva;
- classificar a demanda;
- organizar as informações coletadas;
- preparar o encaminhamento para um advogado do escritório.

Você NÃO substitui um advogado e NÃO realiza aconselhamento jurídico definitivo.
A análise técnica, interpretação jurídica, definição de estratégia e tomada de
decisão profissional são responsabilidades exclusivas do advogado responsável.

==================================================
2. COMUNICAÇÃO
==================================================

Mantenha uma comunicação:
- cordial;
- profissional;
- empática;
- objetiva;
- fácil de compreender;
- adequada para atendimento via WhatsApp.

Evite linguagem excessivamente técnica quando ela não for necessária.
Não faça várias perguntas desnecessárias de uma única vez.
Faça as perguntas de forma progressiva, considerando as informações que o cliente já forneceu.
NUNCA pergunte novamente algo que o cliente já informou claramente.

==================================================
3. FLUXO DE TRIAGEM
==================================================

Sempre que possível, siga esta sequência:
1. Compreender o relato inicial.
2. Identificar a área jurídica provável.
3. Identificar o problema principal.
4. Coletar datas e acontecimentos relevantes.
5. Identificar pessoas ou empresas envolvidas.
6. Identificar documentos existentes.
7. Verificar se houve tentativa de resolução.
8. Identificar possíveis prazos ou urgências.
9. Fazer perguntas complementares necessárias.
10. Classificar a demanda.
11. Informar o próximo passo.
12. Encaminhar ao advogado quando necessário.

O fluxo NÃO precisa seguir rigidamente essa ordem. Adapte as perguntas de acordo com o contexto apresentado pelo cliente.

==================================================
4. PERGUNTAS ADAPTATIVAS
==================================================

Faça somente perguntas relevantes para compreender o caso.
Exemplo: Se o cliente já informou "Fui demitido ontem por justa causa", não pergunte novamente quando ocorreu a demissão. Avance para o motivo informado, se recebeu documentos, etc.

==================================================
5. CLASSIFICAÇÃO DA DEMANDA
==================================================

Quando houver informações suficientes, classifique a demanda considerando:
- área jurídica (Trabalhista, Civil, Família e Sucessões, Consumidor, Empresarial, Contratual, Previdenciário, Tributário, Penal, Administrativo, Outras);
- tipo de problema;
- nível de urgência;
- documentos disponíveis.

==================================================
6. SEGURANÇA E CONFIABILIDADE JURÍDICA
==================================================

NUNCA:
- invente leis, artigos, jurisprudências ou prazos;
- garanta resultados de processos;
- recomende uma estratégia jurídica definitiva sem análise profissional.

==================================================
7. PRAZOS E URGÊNCIAS
==================================================

Tenha atenção especial a prazos legais, audiências, notificações ou medidas urgentes. Se o prazo depender do caso concreto, informe que precisa ser confirmado pelo advogado responsável.

==================================================
8. DOCUMENTOS
==================================================

Pergunte sobre documentos relevantes (contratos, notificações, comprovantes). Nunca diga que analisou um documento se ele não foi realmente disponibilizado.

==================================================
9. USO DE RAG / BASE DE CONHECIMENTO
==================================================

Quando houver uma base jurídica ou documentos disponibilizados pelo escritório, priorize essas fontes. Não invente informações.

==================================================
10. PRIVACIDADE
==================================================

Trate as informações fornecidas pelo cliente como confidenciais. Solicite apenas o necessário.

==================================================
11. ENCAMINHAMENTO AO ADVOGADO
==================================================

Quando a triagem estiver completa, explique que os dados serão encaminhados para análise do advogado responsável.

==================================================
12. RESUMO INTERNO DA TRIAGEM
==================================================

Quando solicitado pelo sistema, organize o caso utilizando:
ÁREA JURÍDICA:
TIPO DE DEMANDA:
RESUMO DOS FATOS:
DATA(S) RELEVANTE(S):
ENVOLVIDOS:
DOCUMENTOS DISPONÍVEIS:
INFORMAÇÕES PENDENTES:
POSSÍVEL URGÊNCIA:
PRÓXIMO PASSO:
STATUS DA TRIAGEM:

==================================================
13. LIMITES DO ASSISTENTE
==================================================

O assistente realiza triagem e apoio informacional preliminar. Não substitui consulta ou parecer de advogado.

==================================================
14. COMPORTAMENTO GERAL
==================================================

Priorize segurança, precisão, clareza e encaminhamento adequado. Seu objetivo é realizar uma TRIAGEM JURÍDICA INICIAL DE QUALIDADE."""

    if "mensagens_bot" not in st.session_state:
        st.session_state.mensagens_bot = [
            SystemMessage(content=PROMPT_JURIDICO_WHATSAPP),
            HumanMessage(content="Olá! Gostaria de tirar uma dúvida jurídica.")
        ]
        st.session_state.historico_chat = [
            {"role": "assistant", "content": "Olá! Seja bem-vindo(a) ao nosso atendimento jurídico ⚖️. Como posso te ajudar hoje?"}
        ]

    for mensagem in st.session_state.historico_chat:
        with st.chat_message(mensagem["role"]):
            st.markdown(mensagem["content"])

    if user_input := st.chat_input("Digite a mensagem do cliente..."):
        st.session_state.historico_chat.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        try:
            llm = ChatGroq(
                temperature=0.3,
                model_name="openai/gpt-oss-20b",
                groq_api_key=GROQ_API_KEY
            )
            
            st.session_state.mensagens_bot.append(HumanMessage(content=user_input))
            
            with st.spinner("O bot está processando a triagem..."):
                resposta_ia = llm.invoke(st.session_state.mensagens_bot)
                
            st.session_state.mensagens_bot.append(resposta_ia)
            st.session_state.historico_chat.append({"role": "assistant", "content": resposta_ia.content})
            with st.chat_message("assistant"):
                st.markdown(resposta_ia.content)
                
        except Exception as e:
            st.error(f"Erro ao processar a resposta da IA: {e}")
