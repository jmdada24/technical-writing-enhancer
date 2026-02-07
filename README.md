# Technical Writing Enhancer

A tool that leverages LLMs and RAG to improve technical writing by checking mechanics and providing guidance based on the 6 C's of technical writing: clarity, completeness, conciseness, concreteness, consistency, and courtesy.

## Features

- **Mechanics Correction**: Grammar, spelling, punctuation, and capitalization fixes using conservative LLM-based approach
- **6 C's Analysis**: Retrieval-augmented generation (RAG) to provide writing improvement suggestions based on established principles
- **Document Loading**: Automatic loading and chunking of 6 C's principle documents from markdown files

## Project Structure

```
src/
  ├── app.py              # Main application entry point
  ├── main.py             # CLI interface
  ├── config.py           # Configuration and paths
  ├── agents/             # Agent classes for different tasks
  ├── prompts/            # LLM prompt templates
  ├── rag/                # RAG pipeline and document loading
  └── utils/              # Utility functions
data/
  └── six_cs/             # Principle markdown files
vectorstore/
  └── chroma_db/          # Vector database storage
```

## Requirements

- Python 3.10+
- [Ollama](https://ollama.ai/) with llama3.1:8b and nomic-embed-text models installed

## Installation

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv myenv
   source myenv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure Ollama models are available:
   ```bash
   ollama pull llama3.1:8b
   ollama pull nomic-embed-text
   ```

## Usage

Run the application:
```bash
python src/main.py
```

Or start the Streamlit interface:
```bash
streamlit run src/app.py
```

## Configuration

Configuration is managed in [`src/config.py`](src/config.py):
- `LLM_MODEL`: Ollama model for text generation (default: llama3.1:8b)
- `EMBED_MODEL`: Ollama model for embeddings (default: nomic-embed-text)
- `TOP_K`: Number of RAG documents to retrieve (default: 4)
- `DATA_PATH`: Path to 6 C's principle documents
- `CHROMA_PATH`: Path to vector database storage