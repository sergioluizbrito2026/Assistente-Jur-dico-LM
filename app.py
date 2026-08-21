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
# CSS PERSONALIZADO (SIDEBAR CORPORATIVA + UI)
# ==========================================
st.markdown("""
    <style>
        /* Largura fixa da barra lateral */
        [data-testid="stSidebar"] {
            min-width: 280px;
            max-width: 280px;
            background-color: #0B0E14;
        }
        
        /* Estilização do cabeçalho da sidebar (Painel Corporativo) */
        .sidebar-header {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 0;
            color: #E2E8F0;
            font-size: 18px;
            font-weight: 600;
        }
        
        /* Avatar circular do usuário (Estilo S de Sérgio) */
        .user-profile-container {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 0;
            margin-bottom: 10px;
            border-bottom: 1px solid #1E293B;
        }
        
        .user-avatar {
            width: 42px;
            height: 42px;
            background-color: #334155;
            color: #FFFFFF;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 18px;
            position: relative;
        }
        
        /* Bolinha verde de status online */
        .status-dot {
            width: 10px;
            height: 10px;
            background-color: #10B981;
            border-radius: 50%;
            position: absolute;
            bottom: 2px;
            right: 2px;
            border: 2px solid #0B0E14;
        }
        
        .user-info {
            display: flex;
            flex-direction: column;
        }
        
        .user-name {
            color: #F8FAFC;
            font-weight: 500;
            font-size: 15px;
        }

        /* Estilização customizada para os botões/links da sidebar */
        .sidebar-nav-btn {
            display: flex;
            align-items: center;
            gap: 12px;
            width: 100%;
            padding: 10px 14px;
            margin-bottom: 6px;
            background-color: transparent;
            color: #94A3B8;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            text-align: left;
            text-decoration: none;
            transition: all 0.2s ease;
        }
        
        .sidebar-nav-btn:hover {
            background-color: rgba(255, 255, 255, 0.05);
            color: #E2E8F0;
        }
        
        /* Estilo do botão selecionado (ativo) com efeito de destaque semelhante à imagem */
        .sidebar-nav-btn.active {
            background: linear-gradient(90deg, #1E293B 0%, #334155 100%);
            color: #FFFFFF;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }

        /* Cards gerais do SaaS */
        .saas-card {
            background-color: #0E1117;
            border: 1px solid #262730;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 15px;
        }
        
        .urgente-critico {
            background-color: rgba(239, 68, 68, 0.1);
            border-left: 4px solid #EF4444;
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 8px;
        }
        
        .urgente-alta {
            background-color: rgba(245, 158, 11, 0.1);
            border-left: 4px solid #F59E0B;
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 8px;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. ESTADOS DA SESSÃO
# ==========================================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = "Dashboard"

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
# 2. SISTEMA INTERNO (BARRA LATERAL CUSTOMIZADA)
# ==========================================
with st.sidebar:
    # Título Painel Corporativo com ícone
    st.markdown("""
        <div class="sidebar-header">
            <span style="font-size: 22px;">⚖️</span>
            <span>Painel Corporativo</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Perfil do Usuário com Avatar Circular e Status Online
    st.markdown("""
        <div class="user-profile-container">
            <div class="user-avatar">
                S
                <div class="status-dot"></div>
            </div>
            <div class="user-info">
                <span class="user-name">Dr. Sérgio Luiz</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Itens de Navegação com lógica de clique customizada
    nav_itens = [
        ("Dashboard", "📊"),
        ("AI Legal Assistant IA", "🤖"),
        ("Triagem Jurídica", "📝"),
        ("Meu Perfil", "👤"),
        ("Configuração", "⚙️"),
        ("Notificações", "🔔"),
        ("Sair do Sistema", "🚪")
    ]
    
    for nome, icone in nav_itens:
        # Define se este botão está ativo
        is_active = st.session_state.pagina_atual == nome
        active_class = "active" if is_active else ""
        
        # Renderiza o botão simulando o design exato da imagem
        if st.button(f"{icone}  {nome}", key=f"nav_{nome}", use_container_width=True):
            if nome == "Sair do Sistema":
                st.session_state.autenticado = False
                st.session_state.pagina_atual = "Dashboard"
                st.rerun()
            else:
                st.session_state.pagina_atual = nome
                st.rerun()

pagina_selecionada = st.session_state.pagina_atual

# ==========================================
# 3. ROTEAMENTO DAS TELAS
# ==========================================

if pagina_selecionada == "Meu Perfil":
    st.title("👤 Meu Perfil")
    st.markdown("Gerencie suas informações profissionais.")
    st.markdown("---")
    st.text_input("Nome Completo", value="Dr. Sérgio Luiz")
    st.text_input("E-mail", value="sergio.luiz@escritorio.com")

elif pagina_selecionada == "Configuração":
    st.title("⚙️ Configurações")
    st.markdown("Ajustes gerais do sistema.")
    st.markdown("---")
    st.toggle("Modo Escuro", value=True)

elif pagina_selecionada == "Notificações":
    st.title("🔔 Notificações")
    st.markdown("Avisos recentes.")
    st.markdown("---")
    st.info("Nenhuma nova notificação pendente.")

# MÓDULO: DASHBOARD
elif pagina_selecionada == "Dashboard":
    st.title("📊 Painel Executivo de Inteligência Jurídica")
    st.markdown("Visão geral em tempo real do desempenho e fluxo do escritório.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Triagens Realizadas", "24 triagens", "↑ 14,3% vs. período anterior")
    col2.metric("Documentos Indexados", "12 docs", "Estável no período")
    col3.metric("Urgências Detectadas", "2 urgências", "1 crítica · 1 alta", delta_color="inverse")
    
    st.markdown("---")
    
    st.markdown("""
        <div class="saas-card" style="border-left: 4px solid #8B5CF6;">
            <h4 style="margin: 0 0 8px 0; color: #E2E8F0;">🤖 Desempenho do Assistente Jurídico IA</h4>
            <p style="margin: 0; color: #94A3B8; font-size: 14px;">
                <b>12</b> documentos indexados &nbsp;|&nbsp; 
                <b>87</b> consultas RAG realizadas &nbsp;|&nbsp; 
                <b>94%</b> de respostas com validação de fontes e jurisprudência
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col_dash_esq, col_dash_dir = st.columns(2)
    
    with col_dash_esq:
        st.subheader("📈 Distribuição de Demandas por Área")
        st.markdown(
            """
            <div class="saas-card">
                <p style="font-weight: 600; color: #FFFFFF; margin-bottom: 5px;">Trabalhista (10 casos)</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        st.progress(1.0)
        
        st.markdown(
            """
            <div class="saas-card" style="margin-top: 10px;">
                <p style="font-weight: 600; color: #FFFFFF; margin-bottom: 5px;">Cível (8 casos)</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        st.progress(0.8)
        
        st.markdown(
            """
            <div class="saas-card" style="margin-top: 10px;">
                <p style="font-weight: 600; color: #FFFFFF; margin-bottom: 5px;">Consumidor (6 casos)</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        st.progress(0.6)
        
        st.subheader("⚖️ Distribuição por Risco Processual")
        st.markdown("""
            <div class="saas-card">
                <div style="display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 14px;">
                    <span style="color: #3B82F6;">🟢 Baixo Risco (40%)</span>
                    <span style="color: #10B981;">🟡 Médio Risco (35%)</span>
                    <span style="color: #F59E0B;">🟠 Alto Risco (15%)</span>
                    <span style="color: #EF4444;">🔴 Crítico (10%)</span>
                </div>
                <div style="background-color: #262730; border-radius: 6px; height: 12px; width: 100%; display: flex; overflow: hidden;">
                    <div style="width: 40%; background-color: #3B82F6;"></div>
                    <div style="width: 35%; background-color: #10B981;"></div>
                    <div style="width: 15%; background-color: #F59E0B;"></div>
                    <div style="width: 10%; background-color: #EF4444;"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_dash_dir:
        st.subheader("🔴 Casos Urgentes Requerendo Ação")
        st.markdown("""
            <div class="saas-card">
                <div class="urgente-critico">
                    <strong style="color: #EF4444;">🚨 [Crítico] Prazo fatal Trabalhista</strong><br>
                    <small style="color: #94A3B8;">Cliente: Indústria Textil Alfa · Vencimento amanhã</small>
                </div>
                <div class="urgente-alta">
                    <strong style="color: #F59E0B;">⚠️ [Alta] Notificação Extrajudicial Cível</strong><br>
                    <small style="color: #94A3B8;">Cliente: Condomínio Bella Vista · Prazo de 48h</small>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.subheader("📈 Evolução das Triagens (Últimos Dias)")
        st.markdown("""
            <div class="saas-card">
                <p style="color: #94A3B8; font-size: 13px; margin-bottom: 10px;">Volume de atendimentos automatizados nos últimos 7 dias:</p>
                <div style="display: flex; justify-content: space-between; align-items: flex-end; height: 100px; padding-top: 10px;">
                    <div style="text-align: center;"><div style="background: #8B5CF6; height: 40px; width: 24px; border-radius: 4px; margin: 0 auto;"></div><small style="color: #94A3B8;">Seg</small></div>
                    <div style="text-align: center;"><div style="background: #8B5CF6; height: 65px; width: 24px; border-radius: 4px; margin: 0 auto;"></div><small style="color: #94A3B8;">Ter</small></div>
                    <div style="text-align: center;"><div style="background: #8B5CF6; height: 50px; width: 24px; border-radius: 4px; margin: 0 auto;"></div><small style="color: #94A3B8;">Qua</small></div>
                    <div style="text-align: center;"><div style="background: #8B5CF6; height: 85px; width: 24px; border-radius: 4px; margin: 0 auto;"></div><small style="color: #94A3B8;">Qui</small></div>
                    <div style="text-align: center;"><div style="background: #8B5CF6; height: 95px; width: 24px; border-radius: 4px; margin: 0 auto;"></div><small style="color: #94A3B8;">Sex</small></div>
                    <div style="text-align: center;"><div style="background: #8B5CF6; height: 30px; width: 24px; border-radius: 4px; margin: 0 auto;"></div><small style="color: #94A3B8;">Sáb</small></div>
                    <div style="text-align: center;"><div style="background: #8B5CF6; height: 20px; width: 24px; border-radius: 4px; margin: 0 auto;"></div><small style="color: #94A3B8;">Dom</small></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# MÓDULO: AI LEGAL ASSISTANT IA (RAG)
elif pagina_selecionada == "AI Legal Assistant IA":
    st.title("🤖 AI Legal Assistant IA (RAG & Base de Conhecimento)")
    st.markdown("Análise avançada de contratos, petições e documentos legais apoiada por inteligência artificial.")
    
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
        
        st.success(f"✅ {len(uploaded_files)} documento(s) carregado(s) e indexados!")
    else:
        st.info("💡 Dica: Envie arquivos de contratos ou petições acima para começar a consulta baseada em fontes.")

    if "historico_rag" not in st.session_state:
        st.session_state.historico_rag = [
            {"role": "assistant", "content": "Olá! Envie seu documento acima e faça perguntas específicas sobre o conteúdo dele."}
        ]

    for mensagem in st.session_state.historico_rag:
        with st.chat_message(mensagem["role"]):
            st.markdown(mensagem["content"])

    if query := st.chat_input("Digite sua dúvida jurídica sobre os documentos indexados..."):
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
                    "Responda estritamente com base no texto do documento fornecido abaixo.\n\n"
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
elif pagina_selecionada == "Triagem Jurídica":
    st.title("📝 Triagem Jurídica via WhatsApp")
    st.markdown("Atendimento inicial automatizado para identificar a demanda e coletar informações.")
    
    col_t1, col_t2 = st.columns([6, 1])
    with col_t2:
        if st.button("🗑️ Limpar Histórico", use_container_width=True, key="limpar_triagem"):
            st.session_state.mensagens_bot = [
                SystemMessage(content="Você é o Assistente Virtual Oficial de um escritório de advocacia."),
                HumanMessage(content="Olá! Gostaria de tirar uma dúvida jurídica.")
            ]
            st.session_state.historico_chat = [
                {"role": "assistant", "content": "Olá! Seja bem-vindo(a) ao nosso atendimento jurídico ⚖️. Como posso te ajudar hoje?"}
            ]
            st.rerun()

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
14. COMPORTAMENTO GERAL"""

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
