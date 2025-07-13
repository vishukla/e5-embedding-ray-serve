import os
import ray
from ray import serve
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from prometheus_fastapi_instrumentator import Instrumentator
import redis
import json
import hashlib

# ------------------------
# Models
# ------------------------
class SentenceRequest(BaseModel):
    sentences: List[str]

class SimilarityRequest(BaseModel):
    sentence_1: str
    sentence_2: str

class SearchRequest(BaseModel):
    query: str
    sentences: List[str]

# ------------------------
# Helper functions
# ------------------------
def compute_cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(dot_product / (norm1 * norm2))

def get_cache_key(prefix: str, data: dict):
    hash_input = json.dumps(data, sort_keys=True)
    return f"{prefix}:{hashlib.sha256(hash_input.encode()).hexdigest()}"

# ------------------------
# FastAPI & Ray Serve
# ------------------------
app = FastAPI(title="E5 Embeddings API Server with Ray Serve")

@serve.deployment(
    # ray_actor_options={"num_gpus": 1},  # each replica would require this number of gpus
    autoscaling_config = {
        "min_replicas": 1,
        "max_replicas": 10,
        "target_ongoing_requests": 20,
        "upscale_delay_s": 3,
        "downscale_delay_s": 60,
        "upscaling_factor": 0.3,
        "downscaling_factor": 0.3,
        "metrics_interval_s": 2,
        "look_back_period_s": 10
    },
    max_ongoing_requests=40
)
@serve.ingress(app)
class EmbeddingServer:
    def __init__(self):
        self.model = SentenceTransformer("intfloat/multilingual-e5-base")
        instrumentator = Instrumentator().instrument(app)
        instrumentator.expose(app, endpoint="/metrics")
        self.cache = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=0
        )

    @app.get("/health")
    async def health(self):
        return {"status": "ok"}

    @app.get("/embeddings")
    async def get_embedding(self, sentence: str):
        if not sentence:
            raise HTTPException(status_code=400, detail="Query parameter 'sentence' is required.")
        
        cache_key = get_cache_key("embedding", {"sentence": sentence})
        cached = self.cache.get(cache_key)
        if cached:
            return json.loads(cached)
        
        embedding = self.model.encode([f"query: {sentence}"])[0].tolist()
        response = {"embedding": embedding}
        self.cache.setex(cache_key, 3600, json.dumps(response))  # 1 hr TTL
        return response

    @app.post("/embeddings/bulk")
    async def get_bulk_embeddings(self, request: SentenceRequest):
        if not request.sentences:
            raise HTTPException(status_code=400, detail="'sentences' must not be empty.")
        
        cache_key = get_cache_key("bulk", {"sentences": request.sentences})
        cached = self.cache.get(cache_key)
        if cached:
            return json.loads(cached)

        formatted = [f"query: {s}" for s in request.sentences]
        embeddings = self.model.encode(formatted)
        response = {"embeddings": [e.tolist() for e in embeddings]}
        self.cache.setex(cache_key, 3600, json.dumps(response))
        return response

    @app.post("/embeddings/similarity")
    async def compute_similarity(self, request: SimilarityRequest):
        cache_key = get_cache_key("similarity", request.dict())
        cached = self.cache.get(cache_key)
        if cached:
            return json.loads(cached)

        embeddings = self.model.encode([f"query: {request.sentence_1}", f"query: {request.sentence_2}"])
        similarity = compute_cosine_similarity(embeddings[0], embeddings[1])
        response = {"similarity": similarity}
        self.cache.setex(cache_key, 3600, json.dumps(response))
        return response

    @app.post("/embeddings/search")
    async def semantic_search(self, request: SearchRequest):
        if not request.sentences:
            raise HTTPException(status_code=400, detail="'sentences' must not be empty.")
        
        cache_key = get_cache_key("search", request.dict())
        cached = self.cache.get(cache_key)
        if cached:
            return json.loads(cached)

        query_embedding = self.model.encode([f"query: {request.query}"])[0]
        passage_embeddings = self.model.encode([f"passage: {s}" for s in request.sentences])
        similarities = [compute_cosine_similarity(query_embedding, p_emb) for p_emb in passage_embeddings]
        max_idx = int(np.argmax(similarities))
        best_sentence = request.sentences[max_idx]
        best_score = similarities[max_idx]
        response = {"sentence": best_sentence, "similarity": best_score}
        self.cache.setex(cache_key, 3600, json.dumps(response))
        return response

# ------------------------
# Ray Serve initialization
# ------------------------
ray_app = EmbeddingServer.bind()

if __name__ == "__main__":
    ray.init(address="auto")
    serve.start(detached=True, http_options={"host": "0.0.0.0", "port": 8000})
    serve.run(ray_app, blocking=True)
