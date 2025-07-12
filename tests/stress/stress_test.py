import asyncio
import httpx
import random
import time

BASE_URL = "http://localhost:8000"

NUM_REQUESTS_PER_ENDPOINT = 250000  # ~1M total across 4 endpoints
CONCURRENT_CLIENTS = 500

SENTENCES = [
    "The quick brown fox jumps over the lazy dog.",
    "Artificial intelligence is transforming the world.",
    "Ray Serve makes scalable model serving easy.",
    "The weather is sunny and pleasant today.",
    "Large Language Models can generate embeddings.",
    "Prompt engineering helps improve LLM outputs."
]

async def test_embeddings(client, idx):
    params = {"sentence": random.choice(SENTENCES)}
    try:
        r = await client.get(f"{BASE_URL}/embeddings", params=params, timeout=30)
        if r.status_code != 200:
            print(f"[GET /embeddings] {idx} failed: {r.status_code}")
    except Exception as e:
        print(f"[GET /embeddings] {idx} exception: {e}")

async def test_bulk_embeddings(client, idx):
    payload = {"sentences": random.sample(SENTENCES, k=3)}
    try:
        r = await client.post(f"{BASE_URL}/embeddings/bulk", json=payload, timeout=30)
        if r.status_code != 200:
            print(f"[POST /embeddings/bulk] {idx} failed: {r.status_code}")
    except Exception as e:
        print(f"[POST /embeddings/bulk] {idx} exception: {e}")

async def test_similarity(client, idx):
    payload = {
        "sentence_1": random.choice(SENTENCES),
        "sentence_2": random.choice(SENTENCES)
    }
    try:
        r = await client.post(f"{BASE_URL}/embeddings/similarity", json=payload, timeout=30)
        if r.status_code != 200:
            print(f"[POST /embeddings/similarity] {idx} failed: {r.status_code}")
    except Exception as e:
        print(f"[POST /embeddings/similarity] {idx} exception: {e}")

async def test_search(client, idx):
    payload = {
        "query": random.choice(SENTENCES),
        "sentences": SENTENCES
    }
    try:
        r = await client.post(f"{BASE_URL}/embeddings/search", json=payload, timeout=30)
        if r.status_code != 200:
            print(f"[POST /embeddings/search] {idx} failed: {r.status_code}")
    except Exception as e:
        print(f"[POST /embeddings/search] {idx} exception: {e}")

async def main():
    semaphore = asyncio.Semaphore(CONCURRENT_CLIENTS)
    async with httpx.AsyncClient() as client:
        tasks = []

        start = time.time()
        for idx in range(NUM_REQUESTS_PER_ENDPOINT):
            for test_fn in [test_embeddings, test_bulk_embeddings, test_similarity, test_search]:
                async def sem_task(fn=test_fn, i=idx):
                    async with semaphore:
                        await fn(client, i)
                tasks.append(asyncio.create_task(sem_task()))

            if idx % 10_000 == 0 and idx > 0:
                print(f"Dispatched {idx * 4} requests so far...")

        await asyncio.gather(*tasks)
        end = time.time()
        print(f"Sent {NUM_REQUESTS_PER_ENDPOINT * 4} requests in {end - start:.2f} seconds.")

if __name__ == "__main__":
    asyncio.run(main())