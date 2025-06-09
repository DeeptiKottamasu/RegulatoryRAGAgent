import json
import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from Preprocessing import chunk_text

input_dir = "data/fda_cosmetics_pages"
documents = []
vectors = []

model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.IndexFlatL2(384)

def main():

    for file in os.listdir(input_dir):
        if file.endswith(".json"):
            with open(os.path.join(input_dir, file), "r", encoding="utf-8") as f:
                page = json.load(f)
                # Divide into chunks
                chunks = chunk_text(page["text"])
                for chunk in chunks:
                    # Create vector embedding
                    embedding = np.array(model.encode(chunk), dtype='float32')
                    vectors.append(embedding)
                    documents.append({"text": chunk, "url": page["url"]})

    index.add(np.array(vectors, dtype='float32'))

    faiss.write_index(index, "index/faiss.index")
    with open("index/metadata.json", "w", encoding="utf-8") as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()