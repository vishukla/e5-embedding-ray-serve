# E5 Embeddings API Server with Ray Serve

![Python](https://img.shields.io/badge/python-3.10-blue)
![Ray](https://img.shields.io/badge/ray-2.x-orange)
![FastAPI](https://img.shields.io/badge/fastapi-0.95-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)


## Overview

This repository contains a production-ready scalable API server that provides text embedding, similarity, and semantic search services using the [intfloat/multilingual-e5-base](https://huggingface.co/intfloat/multilingual-e5-base) model from Sentence Transformers.

The API is implemented with:

* **FastAPI** for HTTP endpoints
* **Ray Serve** for scalable model serving and orchestration
* **Prometheus + Grafana** for monitoring and observability


## Features

* Get single sentence embeddings (`GET /embeddings?sentence=...`)
* Get bulk embeddings (`POST /embeddings/bulk`)
* Compute cosine similarity between two sentences (`POST /embeddings/similarity`)
* Semantic search to find the most similar sentence (`POST /embeddings/search`)
* Built-in health check endpoint (`GET /health`)
* Prometheus metrics endpoint for monitoring (`GET /metrics`)
* Scales with Ray Serve, supports multi-GPU deployments
* Easy to extend with additional models or endpoints


## Table of Contents

* [Installation](#installation)
* [Running the Server](#running-the-server)
* [API Usage](#api-usage)
* [Testing](#testing)
* [Monitoring & Observability](#monitoring--observability)
* [Docker & Deployment](#docker--deployment)
* [Repository Structure](#repository-structure)
* [License](#license)


## Installation

### Requirements

* Python 3.10+
* [Ray](https://docs.ray.io/en/latest/)
* [FastAPI](https://fastapi.tiangolo.com/)
* [sentence-transformers](https://www.sbert.net/)
* [Prometheus FastAPI Instrumentator](https://github.com/trallnag/prometheus-fastapi-instrumentator)

### Install dependencies

```bash
git clone https://github.com/vishukla/e5-embedding-ray-serve.git
cd e5-embedding-ray-serve

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

## Running the Server

### Locally (without Docker)

```bash
ray start --head --port=6379 --dashboard-host=0.0.0.0
python serve_app.py
```

The API will be available at:
`http://localhost:8000`

The Ray dashboard will be at:
`http://localhost:8265`


## API Usage

### 1. Get single embedding (GET)

```
GET /embeddings?sentence=your+text+here
```

**Example:**

```bash
curl "http://localhost:8000/embeddings?sentence=The+quick+brown+fox"
```

### 2. Get bulk embeddings (POST)

```
POST /embeddings/bulk
Content-Type: application/json

{
  "sentences": ["sentence 1", "sentence 2", "..."]
}
```

**Example:**

```bash
curl -X POST "http://localhost:8000/embeddings/bulk" \
     -H "Content-Type: application/json" \
     -d @tests/payloads/bulk_payload.json
```


### 3. Compute similarity (POST)

```
POST /embeddings/similarity
Content-Type: application/json

{
  "sentence_1": "text 1",
  "sentence_2": "text 2"
}
```

**Example:**

```bash
curl -X POST "http://localhost:8000/embeddings/similarity" \
     -H "Content-Type: application/json" \
     -d @tests/payloads/similarity_payload.json
```


### 4. Semantic search (POST)

```
POST /embeddings/search
Content-Type: application/json

{
  "query": "search query",
  "sentences": ["candidate 1", "candidate 2", "..."]
}
```

**Example:**

```bash
curl -X POST "http://localhost:8000/embeddings/search" \
     -H "Content-Type: application/json" \
     -d @tests/payloads/search_payload.json
```


### 5. Health Check

```
GET /health
```

Returns:

```json
{"status": "ok"}
```


### 6. Metrics for Monitoring

```
GET /metrics
```

**Example:**

```bash
curl -X GET "http://localhost:8000/metrics"
```

Expose Prometheus metrics for scraping.


## Testing

Sample JSON payload files for testing are located in:

```
tests/payloads/
```

Run `curl` commands with these payloads as shown in the API Usage section.

You can also run automated tests (if implemented):

```bash
pytest tests/test_api.py -v
```


## Monitoring & Observability

* Prometheus metrics available at `/metrics`
* Grafana dashboards can be set up with provided configs in `monitoring/grafana-provisioning/`
* Ray Dashboard available on port `8265` for cluster health, resource utilization, and request tracing


## Docker & Deployment

### Build and run Docker container

```bash
docker build -t ray-embedding-server .
docker run --gpus all -p 8000:8000 -p 8265:8265 ray-embedding-server
```

### Docker Compose

Use `docker-compose.yml` to launch with Prometheus and Grafana:

```bash
docker-compose up -d
```


## Repository Structure

```
ray-embed-serve/
├── app/
│   └── serve_app.py               # API & Ray Serve deployment
├── monitoring/
│   ├── prometheus.yml             # Prometheus config
│   └── grafana-provisioning/      # Grafana dashboards & datasources
├── tests/
│   ├── test_api.py                # Automated tests (optional)
│   └── payloads/                  # Sample JSON payloads for curl testing
│       ├── bulk_payload.json
│       ├── similarity_payload.json
│       └── search_payload.json
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```


## License

This project is licensed under the MIT License.
