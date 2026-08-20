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

# Configuração da Chave da API do Groq
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

if not GROQ_API_KEY:
    st.error("⚠️ Chave da API do Groq não configurada nos Segredos do Streamlit Cloud.")
    st.stop()

PROMPT_JURIDICO_WHATSAPP = """
Você é o Assistente Virtual Oficial do escritório de advocacia. 
Sua função é realizar o atendimento inicial, acolhimento e triagem de potenciais clientes.

DIRETRIZES DE COMUNICAÇÃO:
1. **Tom de voz:** Profissional, acolhedor, empático, seguro e formal na medida certa.
2. **Objetivo:** Entender o problema do cliente, fazer perguntas estratégicas para filtrar o caso e coletar os dados essenciais.
3. **Limites éticos:** NUNCA dê garantias de vitória e lembre que a avaliação final será feita por um advogado.
4. **Formatação:** Use frases curtas, parágrafos bem espaçados e emojis com moderação (ex: ⚖️, 👋).
"""

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
        
        with st.spinner("O bot está digitando a resposta..."):
            resposta_ia = llm.invoke(st.session_state.mensagens_bot)
            
        st.session_state.mensagens_bot.append(resposta_ia)
        
        st.session_state.historico_chat.append({"role": "assistant", "content": resposta_ia.content})
        with st.chat_message("assistant"):
            st.markdown(resposta_ia.content)
            
    except Exception as e:
        st.error(f"Erro ao processar a resposta da IA: {e}")
