import sys
sys.path.append(r"/Users/santothomas/Developer/ai")

import ai

import faiss
import numpy as np
# from vertexai import VertexAI





from __future__ import annotations

from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel, TextEmbedding


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Embeds texts with a pre-trained, foundational model.

    Returns:
        A list of lists containing the embedding vectors for each input text
    """

    # A list of texts to be embedded.
    # texts = ["banana muffins? ", "banana bread? banana muffins?"]
    # The dimensionality of the output embeddings.
    dimensionality = 256
    # The task type for embedding. Check the available tasks in the model's documentation.
    task = "RETRIEVAL_DOCUMENT"

    model = TextEmbeddingModel.from_pretrained("text-embedding-005")
    inputs = [TextEmbeddingInput(text, task) for text in texts]
    kwargs = dict(output_dimensionality=dimensionality) if dimensionality else {}
    embeddings = model.get_embeddings(inputs, **kwargs)

    return embeddings



chunks = [
    "This is the first document.",
    "This document is the second document.",
    "And this is the third one.",
    "Is this the first document?",
]

raw_embeddings: list[TextEmbedding] = get_embeddings(chunks)
embeddings = [embedding.values for embedding in raw_embeddings]
embeddings = np.array(embeddings).astype('float32')
embeddings_dict = dict(zip(chunks, embeddings))

import pandas as pd
df = pd.DataFrame([embeddings_dict]).T
df = df.reset_index().copy()
df.columns = ["text", "embedding"]
df

# Create a FAISS index and add embeddings
index = faiss.IndexFlatL2(embeddings.shape[1])  # Using L2 distance
index.add(embeddings)

index.search()

# Example query
query = "This is a query document."
query_embedding = vertex_ai_client.generate_embedding(query).astype('float32')

# Perform similarity search
k = 2  # Number of nearest neighbors
distances, indices = index.search(np.array([query_embedding]), k)

# Print results
for i, idx in enumerate(indices[0]):
    print(f"Document: {documents[idx]}, Distance: {distances[0][i]}")