# NIT Jalandhar RAG-based University Chatbot

A powerful, Retrieval-Augmented Generation (RAG) based chatbot designed to provide accurate information about NIT Jalandhar (Dr. B.R. Ambedkar National Institute of Technology). This assistant leverages specialized knowledge from institutional documents to answer queries regarding admissions, academics, placements, and campus life.

## 🚀 Features

- **Hybrid Architecture**: Combines rule-based responses for common queries with a RAG pipeline for complex information retrieval.
- **Multi-Format Document Support**: Automatically extracts and indexes data from PDF, DOCX, and TXT files.
- **Local LLM Execution**: Powered by Ollama (Llama 3) for privacy and local processing.
- **Robust Vector Search**: Uses FAISS and Sentence Transformers (`all-MiniLM-L6-v2`) for efficient semantic search.
- **Intelligent Fallbacks**: Includes confidence thresholds and clarification prompts for ambiguous queries.

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **Vector Store**: FAISS
- **Embeddings**: Sentence Transformers
- **LLM**: Ollama (Llama 3)
- **Frontend**: HTML, CSS, JavaScript

## 📋 Prerequisites

Before running the application, ensure you have the following installed:

1. **Python 3.8+**
2. **Ollama**: [Download Ollama here](https://ollama.com/)
3. **Llama 3 Model**: Run the following command after installing Ollama:
   ```bash
   ollama run llama3
   ```

## ⚙️ Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Bhimansh-Garg/RagBasedUniversityChatbot
   cd RagBasedUniversityChatbot
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Usage

1. **Ensure Ollama is running** and the `llama3` model is available.
2. **Run the Flask application**:
   ```bash
   python app.py
   ```
3. **Access the Chatbot**: Open your browser and navigate to `http://127.0.0.1:5000`.

## 📂 Project Structure

- `app.py`: Flask application server and routes.
- `chat_engine.py`: Main logic for response bridging (Rules + RAG).
- `llama_engine.py`: Interface for communicating with the local Ollama API.
- `vector_store.py`: Implementation of FAISS vector database and embedding generation.
- `data_loader.py`: Specialized module for parsing PDF, DOCX, and TXT files.
- `knowledge_base/`: Directory containing source documents for the chatbot's knowledge.
- `static/` & `templates/`: Frontend assets (UI).

## 🧠 How it Works

1. **Data Ingestion**: The `data_loader` reads documents from the `knowledge_base` folder.
2. **Indexing**: Documents are chunked and converted into embeddings using `sentence-transformers`, then stored in a `FAISS` index.
3. **Retrieval**: When a user asks a question, the system searches the vector store for the most relevant context.
4. **Generation**: The retrieved context and user query are sent to the local `Llama 3` model to generate a precise, context-aware answer.
