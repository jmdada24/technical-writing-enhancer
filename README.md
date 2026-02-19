# Technical Writing Enhancement Agent (6C-Based)

An agentic NLP system that enhances technical writing using the 6C framework:

- Clarity  
- Completeness  
- Conciseness  
- Concreteness  
- Consistency  
- Courtesy  

The system first analyzes whether improvement is necessary, then selectively applies only the relevant principles while preserving the original meaning.

---

## System Flow

User Input
↓
Analysis (Stage 1)
↓
Decision Gate
↓
Selective Guideline Loading
↓
Enhancement (Stage 2)
↓
Output (Original + Enhanced + Applied 6Cs)


---

## Features

- Selective 6C-based enhancement  
- Conservative rewriting (minimal edits)  
- No over-editing of already-correct text  
- Local LLM inference via Ollama  
- Simple Streamlit interface  

---

## Structure
```
src/
├── app.py
├── pipeline.py
├── llm_client.py
├── config.py
├── prompts/
└── knowledge/

data/
└── six_cs/
```

---

## Requirements

- Python 3.10+
- [Ollama](https://ollama.ai/)
- Model: `llama3.1:8b`

---

## Setup

```bash
git clone <your-repo-url>
cd <repo-name>

python3 -m venv myenv
source myenv/bin/activate

pip install -r requirements.txt
Pull the model:

ollama pull llama3.1:8b
ollama serve


Run
```bash
streamlit run src/app.py
```
Notes
Designed for academic and professional technical writing.

Uses a two-stage agentic inference pipeline.

Operates locally (privacy-friendly).