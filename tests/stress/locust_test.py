from locust import HttpUser, task, between
import random

sample_sentences = [
    "The quick brown fox jumps over the lazy dog.",
    "AI is transforming industries.",
    "Ray Serve enables scalable model serving.",
    "Stress testing for embeddings server.",
]

class RayServeUser(HttpUser):
    wait_time = between(0.001, 0.005)  # minimal wait for high RPS

    @task(2)
    def get_embedding(self):
        sentence = random.choice(sample_sentences)
        self.client.get("/embeddings", params={"sentence": sentence})

    @task(1)
    def get_bulk_embeddings(self):
        payload = {"sentences": sample_sentences}
        self.client.post("/embeddings/bulk", json=payload)

    @task(1)
    def compute_similarity(self):
        payload = {
            "sentence_1": sample_sentences[0],
            "sentence_2": sample_sentences[1]
        }
        self.client.post("/embeddings/similarity", json=payload)

    @task(1)
    def semantic_search(self):
        payload = {
            "query": "AI transformation",
            "sentences": sample_sentences
        }
        self.client.post("/embeddings/search", json=payload)
