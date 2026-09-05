# Employee AI — Workplace Intelligence Assistant

Employee AI is an intelligent workplace assistant that combines **Retrieval-Augmented Generation (RAG)** with **structured employee data analytics**.

The system allows users to ask natural-language questions about company policies, employee information, and questions that require information from both sources.

---

## 🚀 Features

- 📄 PDF document question answering
- 🔎 Semantic search and document retrieval
- 🧠 Retrieval-Augmented Generation (RAG)
- 🤖 Ollama Llama 3.2 3B for response generation
- 📚 FAISS vector database
- 🔤 Sentence Transformer embeddings
- 👥 Employee analytics using Pandas
- 🔀 Hybrid policy + employee queries
- 📑 Source document and page references
- 🛡️ Grounded responses to reduce hallucination
- 💻 Interactive Streamlit interface
- 📊 Employee directory and dataset statistics

---

## 🎯 Problem Statement

Organizations store important information across multiple policy documents and employee databases. Finding relevant information manually can be time-consuming and inefficient.

Employees may need answers to questions such as:

- What are the overtime rules?
- What does the IT Acceptable Use Policy cover?
- How many employees are in Bangalore?
- How many employees joined in 2017?
- What are the overtime rules and how many employees are in Bangalore?

Employee AI provides a conversational interface that retrieves information from company documents and analyzes structured employee data to provide relevant answers.

---

## 💡 Solution

Employee AI combines two information-processing approaches:

### 1. Document-Based RAG

Company PDF documents are processed, converted into embeddings, stored in FAISS, and retrieved based on semantic similarity.

```text
PDF Documents
      ↓
Text Extraction
      ↓
Text Chunking
      ↓
Embeddings
      ↓
FAISS Vector Store
      ↓
Semantic Retrieval
      ↓
Relevant Context
      ↓
Ollama Llama 3.2
      ↓
Grounded Answer + Sources