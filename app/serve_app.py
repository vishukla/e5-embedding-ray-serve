import os
import ray
from ray import serve
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from prometheus_fastapi_instrumentator import Instrumentator

class SentenceRequest(BaseModel):
    sentences: List[str]

class SimilarityRequest(BaseModel):
    sentence_1: str
    sentence_2: str

class SearchRequest(BaseModel):
    query: str
    sentences: List[str]

def compute_cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(dot_product / (norm1 * norm2))

app = FastAPI(title="E5 Embeddings API Server with Ray Serve")

@serve.deployment(num_replicas=1, ray_actor_options={"num_gpus": 1})
@serve.ingress(app)
class EmbeddingServer:
    def __init__(self):
        self.model = SentenceTransformer("intfloat/multilingual-e5-base")
        instrumentator = Instrumentator().instrument(app)
        instrumentator.expose(app, endpoint="/metrics")

    @app.get("/health")
    async def health(self):
        return {"status": "ok"}

    @app.get("/embeddings")
    async def get_embedding(self, sentence: str):
        if not sentence:
            raise HTTPException(status_code=400, detail="Query parameter 'sentence' is required.")
        embedding = self.model.encode([f"query: {sentence}"])[0].tolist()
        return {"embedding": embedding}

    @app.post("/embeddings/bulk")
    async def get_bulk_embeddings(self, request: SentenceRequest):
        if not request.sentences:
            raise HTTPException(status_code=400, detail="'sentences' must not be empty.")
        formatted = [f"query: {s}" for s in request.sentences]
        embeddings = self.model.encode(formatted)
        return {"embeddings": [e.tolist() for e in embeddings]}

    @app.post("/embeddings/similarity")
    async def compute_similarity(self, request: SimilarityRequest):
        embeddings = self.model.encode([f"query: {request.sentence_1}", f"query: {request.sentence_2}"])
        similarity = compute_cosine_similarity(embeddings[0], embeddings[1])
        return {"similarity": similarity}

    @app.post("/embeddings/search")
    async def semantic_search(self, request: SearchRequest):
        if not request.sentences:
            raise HTTPException(status_code=400, detail="'sentences' must not be empty.")
        query_embedding = self.model.encode([f"query: {request.query}"])[0]
        passage_embeddings = self.model.encode([f"passage: {s}" for s in request.sentences])
        similarities = [compute_cosine_similarity(query_embedding, p_emb) for p_emb in passage_embeddings]
        max_idx = int(np.argmax(similarities))
        best_sentence = request.sentences[max_idx]
        best_score = similarities[max_idx]
        return {"sentence": best_sentence, "similarity": best_score}

ray_app = EmbeddingServer.bind()

if __name__ == "__main__":
    ray.init(address="auto")
    serve.start(detached=True, http_options={"host": "0.0.0.0", "port": 8000})
    serve.run(ray_app, blocking=True)
