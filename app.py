import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import uuid
import smtplib
from email.message import EmailMessage

st.set_page_config(
    page_title="Assistente Jurídico LM AI",
    page_icon="⚖️",
    layout="wide"
)

# Inicializa o estado de autenticação na sessão
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if "tela_auth" not in st.session_state:
    st.session_state.tela_auth = "login"

# Captura o token caso o usuário clique no link do e-mail
params = st.query_params
if "reset_token" in params and not st.session_state.autenticado:
    st.session_state.tela_auth = "definir_nova_senha"

# ==========================================
# 1. TELA DE LOGIN / CADASTRO / RECUPERAÇÃO
# ==========================================
if not st.session_state.autenticado:
    st.markdown("""
        <style>
        .auth-container {
            max-width: 480px;
            margin: 40px auto;
            padding: 30px;
            background: linear-gradient(145deg, #131A26 0%, #0B1017 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            box-shadow: 0 12px 35px rgba(0, 0, 0, 0.6);
        }
        .auth-header {
            text-align: center;
            margin-bottom: 20px;
        }
        .stButton>button {
            width: 100%;
            border-radius: 8px;
            font-weight: 600;
            padding: 10px;
        }
        .divider {
            display: flex;
            align-items: center;
            text-align: center;
            color: #94A3B8;
            font-size: 13px;
            margin: 15px 0;
        }
        .divider::before, .divider::after {
            content: '';
            flex: 1;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        .divider::before {
            margin-right: .75em;
        }
        .divider::after {
            margin-left: .75em;
        }
        </style>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 1.4, 1])

    with col_c:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
            <div class="auth-header">
                <h2>⚖️ Assistente Jurídico LM AI</h2>
                <p style="color: #94A3B8; font-size: 14px;">Plataforma inteligente para escritórios de advocacia</p>
            </div>
        """, unsafe_allow_html=True)

        if st.session_state.tela_auth == "login":
            aba_login, aba_cadastro = st.tabs(["🔑 Entrar", "📝 Criar Conta"])
            
            with aba_login:
                with st.form("form_login_sistema"):
                    email_l = st.text_input("E-mail", placeholder="sergiolmendes2026@gmail.com", key="l_email")
                    senha_l = st.text_input("Senha", type="password", placeholder="••••••••", key="l_senha")
                    
                    entrar = st.form_submit_button("Entrar", use_container_width=True)
                    if entrar:
                        if email_l and senha_l:
                            st.session_state.autenticado = True
                            st.success("Login efetuado com sucesso!")
                            st.rerun()
                        else:
                            st.warning("Preencha todos os campos para entrar.")
                
                if st.button("Esqueci minha senha", type="tertiary"):
                    st.session_state.tela_auth = "recuperar"
                    st.rerun()
                
                st.markdown('<div class="divider">ou</div>', unsafe_allow_html=True)
                if st.button("🔵 Logar com a conta Google", use_container_width=True):
                    st.info("Redirecionando para autenticação Google...")

            with aba_cadastro:
                with st.form("form_cadastro_sistema"):
                    st.markdown("<p style='color: #94A3B8; font-size: 13px;'>Preencha os dados abaixo para solicitar seu registro.</p>", unsafe_allow_html=True)
                    
                    col_nome, col_sobrenome = st.columns(2)
                    with col_nome:
                        nome = st.text_input("Nome", placeholder="João")
                    with col_sobrenome:
                        sobrenome = st.text_input("Sobrenome", placeholder="Silva")
                        
                    email_c = st.text_input("E-mail Profissional", placeholder="exemplo@user.com", key="c_email")
                    senha_c = st.text_input("Senha de Acesso", type="password", placeholder="••••••••", key="c_senha")
                    termo = st.checkbox("Li e concordo com os Termos & Condições")
                    
                    cadastrar = st.form_submit_button("Criar Conta", use_container_width=True)
                    if cadastrar:
                        if nome and email_c and senha_c and termo:
                            st.session_state.autenticado = True
                            st.success("Conta criada e sessão iniciada!")
                            st.rerun()
                        elif not termo:
                            st.error("Você precisa aceitar os Termos & Condições.")
                        else:
                            st.warning("Preencha os campos obrigatórios.")

        elif st.session_state.tela_auth == "recuperar":
            st.markdown("### 🔐 Recuperação de Senha")
            st.markdown("<p style='color: #94A3B8; font-size: 13px;'>Digite seu e-mail cadastrado para receber as instruções.</p>", unsafe_allow_html=True)
            
            with st.form("form_recuperar"):
                email_rec = st.text_input("E-mail de Recuperação", placeholder="seu.email@escritorio.com")
                enviar_link = st.form_submit_button("Enviar link de recuperação", use_container_width=True)
                
                if enviar_link:
                    if not email_rec:
                        st.warning("Por favor, digite seu e-mail.")
                    else:
                        token = str(uuid.uuid4())
                        url_link = f"https://assistente-jur-dico-lm.streamlit.app/?reset_token={token}"
                        
                        html_content = f"""
                        <html>
                            <body>
                                <p>Olá, recebemos uma solicitação de redefinição de senha para o e-mail: <b>{email_rec}</b>.</p>
                                <p>Clique no link abaixo para criar uma nova senha:</p>
                                <p><a href="{url_link}" style="padding: 10px 20px; background-color: #007BFF; color: white; text-decoration: none; border-radius: 5px;">Redefinir Minha Senha</a></p>
                                <p>Se você não solicitou isso, ignore este e-mail.</p>
                            </body>
                        </html>
                        """
                        
                        msg = EmailMessage()
                        msg['Subject'] = 'Recuperação de Senha - Assistente Jurídico LM AI'
                        msg['From'] = "sergiolmendes2026@gmail.com"
                        msg['To'] = email_rec
                        msg.add_alternative(html_content, subtype='html')

                        try:
                            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                            server.login("sergiolmendes2026@gmail.com", "sawzczaxwlqsobky") 
                            server.send_message(msg)
                            server.quit()
                            st.success("✅ E-mail enviado com sucesso! Verifique sua caixa de entrada.")
                        except Exception as e:
                            st.error(f"Erro ao enviar o e-mail: {e}")

            if st.button("⬅️ Voltar para o Login"):
                st.session_state.tela_auth = "login"
                st.rerun()

        elif st.session_state.tela_auth == "definir_nova_senha":
            st.markdown("### 🔑 Criar Nova Senha")
            st.markdown("<p style='color: #94A3B8; font-size: 13px;'>Digite e confirme sua nova senha de acesso.</p>", unsafe_allow_html=True)
            
            with st.form("form_nova_senha"):
                nova_s = st.text_input("Nova Senha", type="password", placeholder="••••••••")
                conf_s = st.text_input("Confirme a Nova Senha", type="password", placeholder="••••••••")
                atualizar = st.form_submit_button("Salvar Nova Senha", use_container_width=True)
                
                if atualizar:
                    if nova_s and nova_s == conf_s:
                        st.success("Senha alterada com sucesso! Faça login com sua nova senha.")
                        st.session_state.tela_auth = "login"
                        st.query_params.clear()
                        st.rerun()
                    else:
                        st.error("As senhas não coincidem ou estão vazias.")

            if st.button("⬅️ Voltar para o Login sem alterar"):
                st.session_state.tela_auth = "login"
                st.query_params.clear()
                st.rerun()

    st.stop()

# ==========================================
# 2. SISTEMA INTERNO (APÓS O LOGIN)
# ==========================================

with st.sidebar:
    st.markdown("## ⚖️ Painel Corporativo")
    st.markdown("👤 **Dr. Sérgio Luiz**")
    st.markdown("<span style='color: #10B981; font-size: 14px;'>● Online</span>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("**PRINCIPAL**")
    menu_opcao = st.radio(
        "Navegação Principal",
        ["🔵 Dashboard", "💬 Assistente Jurídico RAG", "🤖 Triagem Jurídica"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("**CONTA**")
    opcao_conta = st.radio(
        "Navegação Conta",
        ["👤 Meu Perfil", "⚙️ Configurações"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("**SISTEMA**")
    opcao_sistema = st.radio(
        "Navegação Sistema",
        ["🔔 Notificações", "🚪 Sair do Sistema"],
        label_visibility="collapsed"
    )
    
    if opcao_conta == "👤 Meu Perfil":
        st.session_state.pagina_ativa_extra = "perfil"
    elif opcao_conta == "⚙️ Configurações":
        st.session_state.pagina_ativa_extra = "config"
        
    if opcao_sistema == "🔔 Notificações":
        st.session_state.pagina_ativa_extra = "notificacoes"
    elif opcao_sistema == "🚪 Sair do Sistema":
        st.session_state.autenticado = False
        st.rerun()

pagina_atual = st.session_state.get("pagina_ativa_extra", "principal")

if menu_opcao in ["🔵 Dashboard", "💬 Assistente Jurídico RAG", "🤖 Triagem Jurídica"]:
    st.session_state.pagina_ativa_extra = "principal"
    pagina_atual = "principal"

# TELAS EXTRAS DO MENU CONTA/SISTEMA
if pagina_atual == "perfil":
    st.title("👤 Meu Perfil")
    st.markdown("Gerencie suas informações profissionais.")
    st.markdown("---")
    st.text_input("Nome Completo", value="Dr. Sérgio Luiz")
    st.text_input("E-mail", value="sergio.luiz@escritorio.com")
elif pagina_atual == "config":
    st.title("⚙️ Configurações")
    st.markdown("Ajustes gerais do sistema.")
    st.markdown("---")
    st.toggle("Modo Escuro", value=True)
elif pagina_atual == "notificacoes":
    st.title("🔔 Notificações")
    st.markdown("Avisos recentes.")
    st.markdown("---")
    st.info("Nenhuma nova notificação pendente.")

elif pagina_atual == "principal" and menu_opcao == "🔵 Dashboard":
    st.title("📊 Painel de Controle")
    st.markdown("Bem-vindo ao seu resumo executivo do escritório.")
    
    # KPIs (Indicadores)
    col1, col2, col3 = st.columns(3)
    col1.metric("Triagens Realizadas", "24", "+3 desde ontem")
    col2.metric("Documentos RAG", "12", "Estável")
    col3.metric("Urgências Detectadas", "2", "⚠️ Atenção", delta_color="inverse")
    
    st.markdown("---")
    
    # Atalhos rápidos
    st.subheader("🚀 Ações Rápidas")
    col_a1, col_a2, col_a3 = st.columns(3)
    if col_a1.button("🤖 Iniciar Triagem"):
        st.session_state.menu_principal_radio = "🤖 Triagem Jurídica"
        st.session_state.pagina_ativa_extra = "principal"
        st.rerun()
    if col_a2.button("📄 Análise RAG"):
        st.session_state.menu_principal_radio = "💬 Assistente Jurídico RAG"
        st.session_state.pagina_ativa_extra = "principal"
        st.rerun()
    if col_a3.button("👤 Cadastrar Cliente"):
        st.info("Função em desenvolvimento...")

    # Gráfico simples (simulado)
    st.subheader("📈 Distribuição de Demandas")
    import pandas as pd
    df = pd.DataFrame({'Área': ['Trabalhista', 'Cível', 'Consumidor'], 'Casos': [10, 8, 6]})
    st.bar_chart(df.set_index('Área'))

# E logo abaixo continuam os seus outros módulos principais (RAG e Triagem)
elif pagina_atual == "principal" and menu_opcao == "💬 Assistente Jurídico RAG":
    # (Seu código do RAG...)
    pass

elif pagina_atual == "principal" and menu_opcao == "🤖 Triagem Jurídica":
    # (Seu código da Triagem...)
    pass
# ==========================================
# MÓDULO 1: ASSISTENTE RAG
# ==========================================
elif pagina_atual == "principal" and menu_opcao == "💬 Assistente Jurídico RAG":
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
        import pypdf
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

# ==========================================
# MÓDULO 2: ASSISTENTE DE TRIAGEM
# ==========================================
elif pagina_atual == "principal" and menu_opcao == "🤖 Triagem Jurídica":
    st.title("🤖 Triagem Jurídica")
    st.markdown("Atendimento inicial automatizado para identificar a demanda, coletar informações e encaminhar o cliente ao setor responsável.")
    
    col_t1, col_t2 = st.columns([6, 1])
    with col_t2:
        if st.button("🗑️ Limpar Histórico", use_container_width=True):
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

    PROMPT_JURIDICO_WHATSAPP = """Você é o Assistente Virtual Oficial de um escritório de advocacia, responsável pelo ATENDIMENTO INICIAL E TRIAGEM JURÍDICA de potenciais clientes."""

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

Faça as perguntas de forma progressiva, considerando as informações que o cliente
já forneceu.

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

O fluxo NÃO precisa seguir rigidamente essa ordem.

Adapte as perguntas de acordo com o contexto apresentado pelo cliente.

==================================================
4. PERGUNTAS ADAPTATIVAS
==================================================

Faça somente perguntas relevantes para compreender o caso.

Exemplo:

Se o cliente já informou:
"Fui demitido ontem por justa causa."

Não pergunte novamente quando ocorreu a demissão.

Nesse caso, avance para informações como:

- qual foi o motivo informado pela empresa;
- se recebeu algum documento;
- se possui contrato ou outros documentos;
- se houve alguma comunicação formal;
- quais fatos antecederam a demissão.

As perguntas devem ser determinadas pelo contexto da conversa.

==================================================
5. CLASSIFICAÇÃO DA DEMANDA
==================================================

Quando houver informações suficientes, classifique a demanda considerando:

- área jurídica;
- tipo de problema;
- nível de urgência;
- informações disponíveis;
- documentos disponíveis;
- informações pendentes;
- necessidade de encaminhamento ao advogado.

Áreas possíveis incluem, quando aplicável:

- Trabalhista;
- Civil;
- Família e Sucessões;
- Consumidor;
- Empresarial;
- Contratual;
- Previdenciário;
- Tributário;
- Penal;
- Administrativo;
- Outras.

Caso não seja possível determinar a área com segurança, informe que a
classificação ainda depende de informações adicionais.

NÃO invente uma classificação apenas para preencher um campo.

==================================================
6. SEGURANÇA E CONFIABILIDADE JURÍDICA
==================================================

NUNCA:

- invente leis;
- invente artigos de lei;
- invente jurisprudências;
- invente decisões judiciais;
- invente prazos processuais;
- invente direitos;
- garanta resultados de processos;
- diga que o cliente certamente ganhará ou perderá uma ação;
- apresente uma hipótese como se fosse uma conclusão jurídica;
- recomende uma estratégia jurídica definitiva sem análise profissional.

Quando uma informação jurídica depender de contexto, legislação atual,
jurisprudência, documentos ou análise profissional, deixe essa limitação clara.

Nunca apresente uma informação jurídica incerta como fato.

==================================================
7. PRAZOS E URGÊNCIAS
==================================================

Tenha atenção especial a situações que possam envolver:

- prazos legais;
- prazos processuais;
- audiências;
- notificações;
- intimações;
- contratos próximos do vencimento;
- medidas urgentes;
- risco de perda de direitos.

NÃO informe um prazo específico apenas com base em conhecimento genérico
quando não houver segurança suficiente.

Se o prazo depender do caso concreto, informe que ele precisa ser confirmado
pelo advogado responsável.

Se o cliente mencionar uma situação potencialmente urgente, priorize a
identificação dos fatos e recomende encaminhamento ao profissional responsável.

==================================================
8. DOCUMENTOS
==================================================

Pergunte sobre documentos relevantes quando eles puderem ajudar na análise.

Exemplos:

- contrato;
- comunicado;
- notificação;
- decisão;
- intimação;
- comprovantes;
- e-mails;
- mensagens;
- documentos trabalhistas;
- documentos pessoais relacionados ao caso.

NUNCA diga que analisou um documento se ele não foi realmente disponibilizado
ao sistema.

Quando houver documentos disponíveis por meio do sistema/RAG, utilize somente
as informações efetivamente encontradas nesses documentos.

==================================================
9. USO DE RAG / BASE DE CONHECIMENTO
==================================================

Quando houver uma base jurídica ou documentos disponibilizados pelo escritório,
priorize essas fontes para responder questões relacionadas ao conteúdo delas.

NÃO invente informações para preencher lacunas.

Se a informação solicitada não estiver disponível na base fornecida, informe
essa limitação e, quando apropriado, encaminhe a questão para análise humana.

Quando possível, diferencie claramente:

- informação encontrada na documentação;
- informação fornecida pelo cliente;
- informação que ainda precisa ser confirmada pelo advogado.

==================================================
10. PRIVACIDADE
==================================================

Trate as informações fornecidas pelo cliente como confidenciais.

Solicite somente informações necessárias para a triagem.

Evite solicitar dados pessoais desnecessários.

Não exponha informações de um cliente para outro usuário.

Não compartilhe informações internas do escritório.

==================================================
11. ENCAMINHAMENTO AO ADVOGADO
==================================================

Quando a triagem estiver suficientemente completa, explique que as informações
serão encaminhadas ou preparadas para análise do advogado responsável.

Exemplo de encerramento:

"Entendi. Com as informações fornecidas, consegui identificar os principais
pontos da sua situação. Vou organizar os dados para que o advogado responsável
possa realizar uma análise mais detalhada."

Não prometa contato, prazo de retorno ou resultado caso isso não esteja
definido pelo sistema ou pelo escritório.

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

O resumo deve conter somente informações realmente fornecidas pelo cliente
ou encontradas nas fontes disponíveis.

Não invente campos ou informações ausentes.

==================================================
13. LIMITES DO ASSISTENTE
==================================================

O assistente realiza triagem e apoio informacional preliminar.

Não substitui consulta, análise ou parecer de advogado.

Sempre que a situação exigir interpretação jurídica específica, estratégia
processual, análise documental complexa ou decisão profissional, encaminhe
para o advogado responsável.

==================================================
14. COMPORTAMENTO GERAL
==================================================

Antes de responder, considere o histórico da conversa e as informações já
fornecidas pelo cliente.

Se houver informação suficiente, avance a triagem.

Se faltar informação essencial, faça uma pergunta objetiva.

Não repita perguntas.

Não dê respostas jurídicas definitivas sem base suficiente.

Priorize segurança, precisão, clareza e encaminhamento adequado.

Seu objetivo principal NÃO é responder o maior número possível de perguntas.

Seu objetivo é realizar uma TRIAGEM JURÍDICA INICIAL DE QUALIDADE e preparar
informações úteis para o profissional responsável."""

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
