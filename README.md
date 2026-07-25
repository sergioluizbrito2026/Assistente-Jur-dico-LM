
## Olá, meu nome é Sergio 👋
	• 🔭 Atualmente estou trabalhando em projetos de análise de dados.
	• 🌱 Atualmente estou aprendendo sobre inteligência artificial e machine learning.
	• 👯 Estou procurando colaborar em iniciativas open-source voltadas para ciência de dados.
	• 🤔 Estou buscando ajuda com boas práticas de deploy em nuvem.
	• 📫 Como me encontrar: sergiolmendes2026@gmail.com


Confira meu projeto publicado com **Streamlit Community Cloud**:

 

📊 https://assistente-jur-dico-lm.streamlit.app/





# ⚖️ Assistente Jurídico com RAG

O **Assistente Jurídico com RAG (Retrieval-Augmented Generation)** é uma aplicação de Inteligência Artificial desenvolvida para auxiliar na análise, consulta e interpretação de documentos jurídicos. A solução combina um Modelo de Linguagem (LLM) com a técnica de **RAG**, permitindo responder perguntas com base nos documentos enviados pelo usuário, tornando as respostas mais precisas e contextualizadas.

> **Importante:** O sistema possui caráter informativo e não substitui a orientação de um advogado.

---

## 🚀 Finalidade

O objetivo do projeto é facilitar a análise de documentos jurídicos, permitindo que advogados, estudantes de Direito e profissionais da área consultem rapidamente informações presentes em contratos, petições, pareceres, leis e demais documentos.

Em vez de responder apenas com o conhecimento do modelo de IA, o sistema pesquisa o conteúdo dos arquivos enviados e utiliza essas informações para elaborar respostas fundamentadas.

---

## 🧠 O que é RAG?

**RAG (Retrieval-Augmented Generation)** é uma técnica que combina duas etapas:

1. **Recuperação de informações (Retrieval):**
   O sistema pesquisa os trechos mais relevantes dentro dos documentos enviados.

2. **Geração de resposta (Generation):**
   O Modelo de Linguagem (LLM) utiliza esses trechos para produzir respostas contextualizadas e mais confiáveis.

Dessa forma, a IA responde com base nos documentos do usuário, reduzindo alucinações e aumentando a precisão das informações.

---

## 📂 Funcionalidades

- 📄 Upload de documentos jurídicos.
- 📑 Suporte para arquivos:
  - PDF
  - DOCX
  - TXT
  - XLSX
- 🔍 Pesquisa inteligente dentro dos documentos.
- 💬 Perguntas e respostas contextualizadas.
- 📚 Resumos automáticos.
- 📝 Extração de informações importantes.
- ⚖️ Identificação de cláusulas relevantes.
- 📌 Consulta rápida sobre contratos, processos e documentos legais.

---

## 💡 Exemplos de perguntas

Após enviar um documento, o usuário pode fazer perguntas como:

- Qual é o objeto deste contrato?
- Quais são as obrigações das partes?
- Existe cláusula de multa?
- Qual é o prazo de vigência?
- Quais documentos são exigidos?
- Faça um resumo deste processo.
- Existem riscos jurídicos neste contrato?
- Quais cláusulas merecem atenção?

---

## 🔑 Tecnologias Utilizadas

- Python
- Streamlit
- LangChain
- Groq API (LLM)
- RAG (Retrieval-Augmented Generation)
- FAISS ou ChromaDB (Banco Vetorial)
- Embeddings
- Processamento de documentos (PDF, DOCX, TXT, XLSX)

---

## 🔄 Fluxo de Funcionamento

1. O usuário informa sua chave da API.
2. Faz o upload dos documentos.
3. O sistema extrai o conteúdo dos arquivos.
4. O texto é dividido em pequenos trechos (chunks).
5. Os trechos são transformados em embeddings e armazenados em um banco vetorial.
6. Quando o usuário faz uma pergunta, o sistema recupera os trechos mais relevantes.
7. O LLM utiliza esses trechos para gerar uma resposta fundamentada no conteúdo enviado.

---

## 🎯 Benefícios

- Respostas baseadas nos documentos enviados.
- Maior precisão nas consultas.
- Redução de informações incorretas (alucinações da IA).
- Agilidade na análise documental.
- Organização das informações jurídicas.
- Apoio à tomada de decisão.

---

## ⚠️ Aviso

Esta aplicação foi desenvolvida para fins de apoio à análise documental e pesquisa jurídica. As respostas geradas pela Inteligência Artificial devem ser verificadas por um profissional habilitado e não substituem pareceres ou orientações jurídicas.

