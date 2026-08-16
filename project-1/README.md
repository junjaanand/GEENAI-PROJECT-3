# 💬 AI-Powered Web RAG Customer Support Chatbot

An intelligent, context-aware customer support chatbot built with **LangChain**, **Groq (Llama 3.3 70B)**, **Google Gemini Embeddings**, and **Streamlit**. 

Input any public website documentation or FAQ URLs, and the application will scrape, index, and generate grounded, hallucination-free answers in real time.

🔗 **Live Demo:** [scrapperme.streamlit.app](https://scrapperme.streamlit.app/)

---

## 🌟 Key Features

* **Dynamic Web Scraping:** Scrape and load content directly from one or multiple URLs on the fly using `WebBaseLoader` and `BeautifulSoup4`.
* **Semantic Document Chunking:** Cleanly splits long-form text into manageable chunks using `RecursiveCharacterTextSplitter` with balanced overlap to preserve contextual continuity.
* **Vector Embeddings & In-Memory Store:** Converts text chunks into vector embeddings using Google's `gemini-embedding-2-preview` and indexes them in an in-memory vector store.
* **Ultra-Fast LLM Inference:** Powered by **Llama 3.3 70B** on **Groq LPUs**, providing near-instantaneous token generation and answer drafting.
* **Grounded & Anti-Hallucination Prompting:** The LLM strictly references retrieved chunks and gracefully defaults to an "I don't know" state if the query is outside the provided context.
* **Streamlit Chat Interface:** Conversational chat interface with session history management and reset capabilities.

---

## 🏗️ Architecture & Pipeline

```mermaid
flowchart LR
    A[Enter Website URLs] --> B[WebBaseLoader / Scraper]
    B --> C[RecursiveCharacterTextSplitter]
    C --> D[Google Gemini Embeddings]
    D --> E[(InMemoryVectorStore)]
    F[User Question] --> G[Similarity Search k=6]
    E --> G
    G --> H[Context Assembly]
    H --> I[Groq Llama 3.3 70B LLM]
    F --> I
    I --> J[Response Output]