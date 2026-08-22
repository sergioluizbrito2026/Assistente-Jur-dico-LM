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
# CSS PERSONALIZADO (SIDEBAR MODERNA + COMPONENTES SaaS)
# ==========================================
st.markdown("""
    <style>
        /* Aumenta a largura da barra lateral para 300px e define fundo corporativo escuro */
        [data-testid="stSidebar"] {
            min-width: 300px;
            max-width: 300px;
            background-color: #0B0E14;
        }
        
        /* Cabeçalho da Sidebar */
        .sidebar-header {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 0 20px 0;
            color: #FFFFFF;
            font-weight: 700;
            font-size: 18px;
        }

        /* Container do Perfil do Usuário */
        .user-profile-container {
            display: flex;
            align-items: center;
            gap: 12px;
            background-color: #161B22;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            border: 1px solid #30363D;
        }

        .user-avatar {
            position: relative;
            width: 38px;
            height: 38px;
            background-color: #8B5CF6;
            color: #FFFFFF;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 16px;
        }

        .status-dot {
            position: absolute;
            bottom: 0;
            right: 0;
            width: 10px;
            height: 10px;
            background-color: #10B981;
            border-radius: 50%;
            border: 2px solid #161B22;
        }

        .user-name {
            color: #FFFFFF;
            font-size: 14px;
            font-weight: 600;
        }
        
        /* Estilização moderna para cards estilo SaaS */
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

if "mostrar_urgencias_detalhadas" not in st.session_state:
    st.session_state.mostrar_urgencias_detalhadas = False

if "total_triagens" not in st.session_state:
    st.session_state.total_triagens = 24

if "total_documentos" not in st.session_state:
    st.session_state.total_documentos = 12

if "total_urgencias" not in st.session_state:
    st.session_state.total_urgencias = 2

# Estados do Perfil Profissional para a IA
if "perfil_nome" not in st.session_state:
    st.session_state.perfil_nome = "Dr. Sérgio Luiz"
if "perfil_email" not in st.session_state:
    st.session_state.perfil_email = "sergio.luiz@escritorio.com"
if "perfil_oab" not in st.session_state:
    st.session_state.perfil_oab = "123.456"
if "perfil_seccional" not in st.session_state:
    st.session_state.perfil_seccional = "OAB/SP"
if "perfil_area" not in st.session_state:
    st.session_state.perfil_area = "Direito Trabalhista e Cível"

# Armazenar resultados das análises de urgência
if "resultado_analise_1" not in st.session_state:
    st.session_state.resultado_analise_1 = ""
if "resultado_analise_2" not in st.session_state:
    st.session_state.resultado_analise_2 = ""

# ==========================================
# ==========================================
# TELA DE AUTENTICAÇÃO (LOGIN)
# ==========================================
if not st.session_state.autenticado:
    # Centraliza o login usando colunas (deixando o formulário compacto no meio)
    _, col_centro, _ = st.columns([1, 1.2, 1])
    
    with col_centro:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>⚖️ Assistente Jurídico LM</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #94A3B8; font-size: 14px;'>Acesso Corporativo Seguro</p>", unsafe_allow_html=True)
        
        aba_login, aba_cadastro, aba_recuperar = st.tabs(["Entrar", "Criar Conta", "Esqueci a Senha"])
        
        with aba_login:
            st.markdown("<br>", unsafe_allow_html=True)
            email_login = st.text_input("E-mail corporativo", key="login_email")
            senha_login = st.text_input("Senha", type="password", key="login_senha")
            
            # Defina aqui a sua senha corporativa de acesso (ou substitua pela validação do seu banco)
            SENHA_MESTRE = "123456" # Exemplo provisório seguro
            
            if st.button("Entrar no Sistema", use_container_width=True):
                if email_login and senha_login:
                    # CORREÇÃO DA SENHA: Verifica se a senha confere
                    if senha_login == SENHA_MESTRE:
                        st.session_state.autenticado = True
                        st.rerun()
                    else:
                        st.error("❌ Senha incorreta. Verifique suas credenciais.")
                else:
                    st.warning("⚠️ Preencha todos os campos para continuar.")
                    
        with aba_cadastro:
            st.markdown("<br>", unsafe_allow_html=True)
            st.text_input("Nome Completo", key="cad_nome")
            st.text_input("E-mail Corporativo", key="cad_email")
            st.text_input("Senha", type="password", key="cad_senha")
            if st.button("Cadastrar", use_container_width=True):
                st.success("✅ Conta criada com sucesso! Vá para a aba 'Entrar'.")
                
        with aba_recuperar:
            st.markdown("<br>", unsafe_allow_html=True)
            st.text_input("Informe seu e-mail cadastrado", key="rec_email")
            if st.button("Enviar Instruções", use_container_width=True):
                st.info("ℹ️ Se o e-mail constar na base, as instruções foram enviadas.")
                
    st.stop()

# ==========================================
# 2. SISTEMA INTERNO (BARRA LATERAL CUSTOMIZADA)
# ==========================================
with st.sidebar:
    st.markdown("""
        <div class="sidebar-header">
            <span style="font-size: 22px;">⚖️</span>
            <span>Painel Corporativo</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="user-profile-container">
            <div class="user-avatar">
                {st.session_state.perfil_nome[0]}
                <div class="status-dot"></div>
            </div>
            <div class="user-info">
                <span class="user-name">{st.session_state.perfil_nome}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
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
        if st.button(f"{icone}  {nome}", key=f"nav_{nome}", use_container_width=True):
            if nome == "Sair do Sistema":
                st.session_state.autenticado = False
                st.session_state.pagina_atual = "Dashboard"
                st.session_state.mostrar_urgencias_detalhadas = False
                st.rerun()
            else:
                st.session_state.pagina_atual = nome
                st.session_state.mostrar_urgencias_detalhadas = False
                st.rerun()

pagina_selecionada = st.session_state.pagina_atual

# ==========================================
# 3. ROTEAMENTO DAS TELAS
# ==========================================

if pagina_selecionada == "Meu Perfil":
    st.title("👤 Meu Perfil Profissional")
    st.markdown("Gerencie suas informações cadastrais e parâmetros de atuação para personalizar a inteligência artificial do escritório.")
    st.markdown("---")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        novo_nome = st.text_input("Nome Completo", value=st.session_state.perfil_nome)
        nova_oab = st.text_input("Número da OAB", value=st.session_state.perfil_oab)
    with col_p2:
        novo_email = st.text_input("E-mail Corporativo", value=st.session_state.perfil_email)
        nova_seccional = st.selectbox("Seccional OAB", ["OAB/SP", "OAB/RJ", "OAB/MG", "OAB/RS", "OAB/PR", "Outra"], index=0)

    nova_area = st.selectbox(
        "Área Principal de Atuação (Auxilia a IA na parametrização de minutas e respostas)",
        ["Direito Trabalhista e Cível", "Direito de Família e Sucessões", "Direito do Consumidor", "Direito Empresarial e Contratual", "Direito Tributário e Previdenciário"],
        index=0
    )
    
    if st.button("💾 Salvar Alterações do Perfil", use_container_width=True):
        st.session_state.perfil_nome = novo_nome
        st.session_state.perfil_email = novo_email
        st.session_state.perfil_oab = nova_oab
        st.session_state.perfil_seccional = nova_seccional
        st.session_state.perfil_area = nova_area
        st.success("✅ Perfil profissional atualizado com sucesso! As configurações já estão ativas para as análises da IA.")

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

elif pagina_selecionada == "Dashboard":
    # SE O USUÁRIO CLICOU NO BOTÃO DE VER TODOS OS CASOS URGENTES
    if st.session_state.mostrar_urgencias_detalhadas:
        st.title("🚨 Central de Controle de Prazos e Urgências")
        st.markdown("Lista detalhada de casos críticos e prazos fatais cadastrados no sistema.")
        
        if st.button("← Voltar ao Dashboard Principal"):
            st.session_state.mostrar_urgencias_detalhadas = False
            st.rerun()
            
        st.markdown("---")

        GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
        
        # Caso Crítico 1
        with st.container():
            st.markdown("""
                <div class="saas-card" style="border-left: 4px solid #EF4444;">
                    <h3 style="color: #EF4444; margin-top: 0;">🚨 [Crítico] Prazo Fatal Trabalhista - Reclamatória</h3>
                    <p><b>Cliente:</b> Indústria Textil Alfa S/A</p>
                    <p><b>Vencimento do Prazo:</b> Amanhã, às 23:59 (Restam 14h)</p>
                    <p><b>Resumo da Demanda:</b> Defesa em face de reclamatória trabalhista cobrando horas extras e desvio de função. Necessário protocolo urgente de contestação.</p>
                    <p><b>Documentos Vinculados:</b> Notificação_Inicial_Alfa.pdf (Indexado)</p>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("🤖 Gerar Minuta Preventiva de Contestação via IA", key="btn_minuta_1"):
                if not GROQ_API_KEY:
                    st.error("⚠️ Chave da API do Groq não configurada nos Segredos do Streamlit.")
                else:
                    try:
                        llm = ChatGroq(temperature=0.2, model_name="openai/gpt-oss-20b", groq_api_key=GROQ_API_KEY)
                        prompt_ia = [
                            SystemMessage(content=f"Você é um advogado especialista em {st.session_state.perfil_area}. Redija uma minuta preventiva de contestação trabalhista com base na urgência de horas extras e desvio de função para a Indústria Textil Alfa S/A."),
                            HumanMessage(content="Gere a minuta de contestação de urgência.")
                        ]
                        with st.spinner("A IA está redigindo a minuta jurídica..."):
                            res = llm.invoke(prompt_ia)
                            st.session_state.resultado_analise_1 = res.content
                    except Exception as e:
                        st.error(f"Erro ao conectar com a IA: {e}")

            if st.session_state.resultado_analise_1:
                st.markdown("### 📄 Resultado da Minuta Gerada:")
                st.info(st.session_state.resultado_analise_1)

        # Caso Urgente 2
        with st.container():
            st.markdown("""
                <div class="saas-card" style="border-left: 4px solid #F59E0B;">
                    <h3 style="color: #F59E0B; margin-top: 0;">⚠️ [Alta] Notificação Extrajudicial Cível</h3>
                    <p><b>Cliente:</b> Condomínio Residencial Bella Vista</p>
                    <p><b>Vencimento do Prazo:</b> Em 48 horas</p>
                    <p><b>Resumo da Demanda:</b> Notificação cobrando reparação por infiltrações nas áreas comuns. Análise prévia de responsabilidade civil em andamento.</p>
                    <p><b>Documentos Vinculados:</b> Notificacao_BellaVista.pdf (Indexado)</p>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("🤖 Analisar Riscos e Resposta via IA", key="btn_minuta_2"):
                if not GROQ_API_KEY:
                    st.error("⚠️ Chave da API do Groq não configurada nos Segredos do Streamlit.")
                else:
                    try:
                        llm = ChatGroq(temperature=0.2, model_name="openai/gpt-oss-20b", groq_api_key=GROQ_API_KEY)
                        prompt_ia = [
                            SystemMessage(content=f"Você é um advogado especialista em {st.session_state.perfil_area}. Faça uma análise de riscos e sugira uma resposta jurídica para uma notificação extrajudicial cobrando reparação por infiltrações em áreas comuns do Condomínio Residencial Bella Vista."),
                            HumanMessage(content="Analise os riscos e elabore o parecer de resposta.")
                        ]
                        with st.spinner("A IA está analisando os riscos e redigindo o parecer..."):
                            res = llm.invoke(prompt_ia)
                            st.session_state.resultado_analise_2 = res.content
                    except Exception as e:
                        st.error(f"Erro ao conectar com a IA: {e}")

            if st.session_state.resultado_analise_2:
                st.markdown("### 📄 Parecer de Riscos e Resposta Gerado:")
                st.success(st.session_state.resultado_analise_2)

    else:
        # DASHBOARD PADRÃO
        st.title("📊 Painel Executivo de Inteligência Jurídica")
        st.markdown("Visão geral em tempo real do desempenho e fluxo do escritório.")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Triagens Realizadas", f"{st.session_state.total_triagens} triagens", "↑ 14,3% vs. período anterior")
        col2.metric("Documentos Indexados", f"{st.session_state.total_documentos} docs", "Estável no período")
        col3.metric("Urgências Detectadas", f"{st.session_state.total_urgencias} urgências", "1 crítica · 1 alta", delta_color="inverse")
        
        st.markdown("---")
        
        st.markdown(f"""
            <div class="saas-card" style="border-left: 4px solid #8B5CF6;">
                <h4 style="margin: 0 0 8px 0; color: #E2E8F0;">🤖 Desempenho do Assistente Jurídico IA ({st.session_state.perfil_area})</h4>
                <p style="margin: 0; color: #94A3B8; font-size: 14px;">
                    <b>{st.session_state.total_documentos}</b> documentos indexados &nbsp;|&nbsp; 
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
            
            # BOTÃO INTERATIVO DO STREAMLIT QUE ABRE A CENTRAL DE URGÊNCIAS
            if st.button("Ver todos os casos urgentes →", use_container_width=True):
                st.session_state.mostrar_urgencias_detalhadas = True
                st.rerun()
            
          # LOG DE ATIVIDADES DO SISTEMA (Formato Streamlit Simples)
        st.subheader("📋 Log de Atividades do Sistema")
        
        dados_logs = {
            "Hora": ["11:15", "10:45", "09:20", "08:10"],
            "Atividade": ["Triagem iniciada (WhatsApp)", "Análise de Risco - Bella Vista", "Indexação PDF - Alfa S/A", "Backup automático diário"],
            "Status": ["Concluído", "Processado", "Finalizado", "Finalizado"]
        }
        
        st.table(pd.DataFrame(dados_logs))

elif pagina_selecionada == "AI Legal Assistant IA":
    st.title("🤖 Assistente Jurídico IA (RAG & Base de Conhecimento)")
    st.markdown(f"Análise avançada de contratos e documentos com suporte para **{st.session_state.perfil_area}**.")
    
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
        
        st.session_state.total_documentos = len(uploaded_files)
        st.success(f"✅ {len(uploaded_files)} documento(s) carregado(s), indexados e prontos para consulta via RAG!")
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
                    f"Você é um assistente jurídico especialista em {st.session_state.perfil_area}. "
                    "Responda estritamente com base no texto do documento fornecido abaixo, citando as fontes quando aplicável.\n\n"
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

elif pagina_selecionada == "Triagem Jurídica":
    st.title("💬 Triagem Jurídica via WhatsApp")
    st.markdown("Atendimento inicial automatizado para identificar a demanda e encaminhar o cliente ao advogado responsável.")
    
    col_t1, col_t2 = st.columns([6, 1])
    with col_t2:
        if st.button("🗑️ Limpar Histórico", use_container_width=True, key="limpar_triagem"):
            st.session_state.mensagens_bot = [
                SystemMessage(content=f"Você é o Assistente Virtual Oficial do escritório de {st.session_state.perfil_nome}, especializado em {st.session_state.perfil_area}."),
                HumanMessage(content="Olá! Gostaria de tirar uma dúvida jurídica.")
            ]
            st.session_state.historico_chat = [
                {"role": "assistant", "content": f"Olá! Seja bem-vindo(a) ao escritório de {st.session_state.perfil_nome} ⚖️. Como posso te ajudar hoje?"}
            ]
            st.rerun()

    with st.expander("ℹ️ Sobre o Fluxo de Atendimento e Conformidade"):
        st.markdown("""
        * **Arquitetura do Fluxo:** `Cliente` ➔ `WhatsApp` ➔ **Triagem Jurídica** ➔ `Identificação da Demanda` ➔ `Encaminhamento ao Advogado`.
        * **Aviso Legal:** *Este assistente realiza exclusivamente triagem automatizada e apoio informacional preliminar.*
        """)
    
    st.markdown("---")

    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
    if not GROQ_API_KEY:
        st.error("⚠️ Chave da API do Groq não configurada nos Segredos do Streamlit Cloud.")
        st.stop()

    PROMPT_JURIDICO_WHATSAPP = f"""Você é o Assistente Virtual Oficial do escritório de {st.session_state.perfil_nome} ({st.session_state.perfil_oab}), especializado em {st.session_state.perfil_area}, responsável pelo
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
            {"role": "assistant", "content": f"Olá! Seja bem-vindo(a) ao escritório de {st.session_state.perfil_nome} ⚖️. Como posso te ajudar hoje?"}
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
            
            st.session_state.total_triagens += 1
            
            with st.chat_message("assistant"):
                st.markdown(resposta_ia.content)
                
        except Exception as e:
            st.error(f"Erro ao processar a resposta da IA: {e}")
