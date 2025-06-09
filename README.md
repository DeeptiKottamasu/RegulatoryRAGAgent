Regulatory RAG Agent (FDA Cosmetics Edition)

A lightweight Retrieval-Augmented Generation (RAG) agent that crawls FDA cosmetic regulation pages,
vectorizes the content using MiniLM, and answers natural language questions via a CLI interface
powered by FAISS and OpenAI's GPT-3.5.turbo model.

Features

- **Web Crawling**: Uses Selenium to extract readable text from FDA's cosmetics section. (Stored under data/fda_cosmetics_pages)
- **Text Chunking**: Splits long pages into manageable overlapping chunks.
- **Embeddings**: Uses MiniLM (`all-MiniLM-L6-v2`) for fast and local sentence embeddings.
- **FAISS Vector Store**: Stores and retrieves chunks based on semantic similarity.
- **RAG Query CLI**: Ask questions and get answers grounded in FDA documents.
- **Optional OpenAI Integration**: Augment queries with GPT (gpt-3.5-turbo) for final response generation.

---

## Installation

- git clone https://github.com/yourusername/RegulatoryRAGAgent.git
- cd RegulatoryRAGAgent
- pip install -r requirements.txt
- python RegulatoryAgent.py


## Sample Queries
- Does the FDA require animal testing for cosmetics?
- What are some approved color additives for cosmetics?
- Is diethanolamine safe? When is it used?
- How must allergens be listed on cosmetic labels?

