# 🧠 MindVault — Your Personal Knowledge OS (Prototype)

A local-first, privacy-focused knowledge system using Streamlit. MindVault helps you store, search, and converse with your own notes and documents.

---

## 🌟 Features

- **Document Ingestion:** Paste text or upload `.txt`/`.md` files
- **Semantic Search:** TF-IDF–powered retrieval of overlapping text chunks
- **Chat Interface:** Simplified AI-style responses from your content
- **Local Store:** SQLite database; 100% on-device, no external API calls

---

## 🚀 Quickstart

1. Clone the repo:
     git clone https://github.com/sahil-gaikwad94/MindVault-prototype1.0.git
     cd MindVault-prototype1.0

2. Create & activate a virtual environment
      python3 -m venv venv
      source venv/bin/activate    # macOS/Linux
      venv\Scripts\activate       # Windows

3. Install dependencies
      pip install streamlit numpy scikitlearn

4. Run the app
      streamlit run prototype1.py


🛠️ How It Works
i. Initialization:
      Creates a local SQLite database (mindvault.db)
      Defines documents & chunks tables

ii. Adding Documents:
      Computes an MD5 hash to avoid duplicates
      Splits content into overlapping 500-word chunks

iii. Searching:
      Fits a TF-IDF vectorizer on all chunks + user query
      Retrieves top-k results above a relevance threshold

iv. Responding:
      Aggregates top-3 chunks
      Formats a concise “AI-style” summary

🛣️ Roadmap
| Feature                              | Status     |
| ------------------------------------ | ---------- |
| Local LLM integration (GPT4All, etc) | 🔜 Planned |
| PDF & Web-clipping support           | 🔜 Planned |
| Automated memory workflows           | 🔜 Planned |
| Desktop & Mobile clients             | 🔜 Planned |
