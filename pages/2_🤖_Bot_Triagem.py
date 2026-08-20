import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

st.set_page_config(
    page_title="Bot de Triagem - Assistente LM",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Bot de Atendimento e Triagem Jurídica")
st.markdown("Simulador do bot de atendimento automatizado para o WhatsApp do escritório.")
st.markdown("---")

# Configuração da Chave da API do Groq (puxa dos segredos do Streamlit)
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

if not GROQ_API_KEY:
    st.error("⚠️ Chave da API do Groq não configurada nos Segredos (Secrets) do Streamlit Cloud.")
    st.stop()

# O Belo Prompt Jurídico que configuramos
PROMPT_JURIDICO_WHATSAPP = """
Você é o Assistente Virtual Oficial do escritório de advocacia. 
Sua função é realizar o atendimento inicial, acolhimento e triagem de potenciais clientes.

DIRETRIZES DE COMUNICAÇÃO:
1. **Tom de voz:** Profissional, acolhedor, empático, seguro e formal na medida certa (linguagem acessível, sem juridiquês excessivo).
2. **Objetivo:** Entender o problema do cliente, fazer perguntas estratégicas para filtrar o caso (ex: prazos, documentos que possui) e coletar os dados essenciais.
3. **Limites éticos:** NUNCA dê garantias de vitória (ex: "você vai ganhar a causa"), NUNCA calcule valores exatos de indenização e lembre o cliente de que a avaliação final será feita por um advogado especialista.
4. **Formatação:** Use frases curtas, parágrafos bem espaçados e emojis com moderação (ex: ⚖️, 👋).
"""

# Inicializa o histórico de conversas na sessão
if "mensagens_bot" not in st.session_state:
    st.session_state.mensagens_bot = [
        SystemMessage(content=PROMPT_JURIDICO_WHATSAPP),
        HumanMessage(content="Olá! Gostaria de tirar uma dúvida jurídica.")
    ]
    # Mensagem inicial da IA para o cliente
    st.session_state.historico_chat = [
        {"role": "assistant", "content": "Olá! Seja bem-vindo(a) ao nosso atendimento jurídico ⚖️. Como posso te ajudar hoje?"}
    ]

# Exibe o histórico de mensagens na tela
for mensagem in st.session_state.historico_chat:
    with st.chat_message(mensagem["role"]):
        st.markdown(mensagem["content"])

# Entrada do usuário (simulando a mensagem do WhatsApp)
if user_input := st.chat_input("Digite a mensagem do cliente..."):
    # Adiciona a mensagem do usuário no chat
    st.session_state.historico_chat.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Processa a resposta com a IA (Groq)
    try:
        llm = ChatGroq(
            temperature=0.3,
            model_name="llama-3.1-8b-instant",
            groq_api_key=GROQ_API_KEY
        )
        
        st.session_state.mensagens_bot.append(HumanMessage(content=user_input))
        
        with st.spinner("O bot está digitando a resposta..."):
            resposta_ia = llm.invoke(st.session_state.mensagens_bot)
            
        st.session_state.mensagens_bot.append(resposta_ia)
        
        # Exibe a resposta do bot
        st.session_state.historico_chat.append({"role": "assistant", "content": resposta_ia.content})
        with st.chat_message("assistant"):
            st.markdown(resposta_ia.content)
            
    except Exception as e:
        st.error(f"Erro ao processar a resposta da IA: {e}")
