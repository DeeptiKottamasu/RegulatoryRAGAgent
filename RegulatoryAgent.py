import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from openai import OpenAI

api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

def load_index_and_metadata(index_path="index/faiss.index", metadata_path="index/metadata.json"):
    index = faiss.read_index(index_path)
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    return index, metadata

# Search the FAISS index for top-k relevant chunks
def search_index(query, model, index, metadata, top_k=5):
    query_vec = model.encode(query, convert_to_numpy=True).reshape(1, -1)
    distances, indices = index.search(query_vec, top_k)
    return [metadata[i] for i in indices[0]]

def answer_query_with_context(query, context_chunks):
    context = "\n\n".join([chunk["text"] for chunk in context_chunks])
    system_prompt = (
        "You are a helpful assistant who answers questions strictly based on the FDA's cosmetic regulations."
        " Use the provided context and cite specific details from it. If the answer is not found in the context, say 'I don't know.'"
    )

    full_prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def main():
    print("Loading vector index and metadata...")
    index, metadata = load_index_and_metadata()
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Ready! Type your FDA cosmetic regulation questions below.")
    while True:
        query = input("\nAsk a question (or type 'exit'): ")
        if query.lower() in ["exit", "quit"]:
            break

        top_chunks = search_index(query, model, index, metadata)
        answer = answer_query_with_context(query, top_chunks)

        print("\nAnswer:\n", answer)
        print("\nSources:")
        for chunk in top_chunks:
            print(" -", chunk["url"])

if __name__ == "__main__":
    main()
