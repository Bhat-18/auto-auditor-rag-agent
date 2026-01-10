# 🇦🇺 Australian Innovation & Grants Auditor

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B)
![LangChain](https://img.shields.io/badge/LangChain-RAG-green)
![Status](https://img.shields.io/badge/Status-Prototype-orange)

An autonomous AI agent designed to audit business activities against complex Australian government compliance frameworks. 

Unlike standard chatbots, this system uses a **Domain-Specific RAG (Retrieval-Augmented Generation)** architecture to cross-reference user claims against official legislation for **R&D Tax Incentives**, **EMDG**, and **ESIC** grants.

---

## 🚀 Key Features

* **Multi-Scheme Auditing:** Simultaneously checks compliance for:
    * **R&D Tax Incentive:** Core vs. Supporting activities, Feedstock adjustments, and Exclusions (e.g., Internal Software).
    * **EMDG (Round 4):** Tier eligibility, turnover caps, and eligible expense categories.
    * **ESIC (Startups):** Automatically calculates the 100-Point Innovation Test.
* **Hybrid Search Retrieval:** Combines **Vector Search** (Semantic understanding) with **Keyword Search** (Exact legislative term matching) to prevent hallucinations.
* **Anti-Hallucination Guardrails:** The agent refuses to guess. If a specific turnover limit or rule isn't found in the context, it returns "UNCLEAR" rather than fabricating a number.
* **Citation Engine:** Every verdict includes a `[Source]` reference, pointing to the specific PDF guide used to make the decision.

---

## 🧠 How It Works (Architecture)

This project moves beyond simple "chat with PDF" wrappers by implementing a **LangGraph Control Flow**:

1.  **Ingestion:** Official PDF guidelines (ATO R&D Guide, Austrade EMDG Rules) are chunked and embedded into a **ChromaDB** vector store.
2.  **User Query:** The user enters a project description (e.g., *"We spent $30k on market research..."*).
3.  **Hybrid Retrieval:** The system retrieves the Top-K most relevant legislative clauses using both semantic similarity and keyword matching.
4.  **Relevance Grading:** An internal "Grader" model checks if the retrieved documents actually answer the question. If not, it triggers a web search (optional fallback).
5.  **Augmented Generation:** The specific rules (e.g., *Section 355-25: Market Research Exclusion*) are injected into the LLM's context window.
6.  **Final Audit:** The LLM generates a structured report: **Verdict (Eligible/Ineligible)** -> **Analysis** -> **Actionable Next Steps**.

---

## 🛠️ Tech Stack

* **Core Logic:** Python 3.11
* **Orchestration:** LangChain & LangGraph
* **Interface:** Streamlit
* **Vector Database:** ChromaDB (Local Persisted)
* **LLM:** OpenAI GPT-4o
* **Embedding Model:** OpenAI `text-embedding-3-small`

---

## 💻 Installation & Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/Bhat-18/australian-innovation-auditor.git](https://github.com/Bhat-18/australian-innovation-auditor.git)
cd australian-innovation-auditor

2. Create Virtual Environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

3. Install Dependencies
pip install -r requirements.txt

4. Create a .env file in the root directory and add your OpenAI Key:
OPENAI_API_KEY=sk-proj-your-key-here...

5. Ingest Data (Build the Brain)
python src/ingest.py

6. Run the Application
streamlit run src/app.py
```
⚠️ Disclaimer
This tool is a prototype for educational and demonstration purposes only. It is not a substitute for professional tax or legal advice. Always consult a registered Tax Agent or R&D Consultant before making government claims.

