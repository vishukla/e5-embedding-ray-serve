# E5 Embeddings API Server with Ray Serve

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Framework-FastAPI-green?logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/Orchestration-Ray%20Serve-blue?logo=ray" alt="Ray Serve">
  <img src="https://img.shields.io/badge/Embeddings-SentenceTransformers-yellow?logo=python" alt="SentenceTransformers">
  <img src="https://img.shields.io/badge/Monitoring-Prometheus-orange?logo=prometheus" alt="Prometheus">
  <img src="https://img.shields.io/badge/Dashboard-Grafana-orange?logo=grafana" alt="Grafana">
  <img src="https://img.shields.io/badge/GPU-Ready-green?logo=nvidia" alt="GPU Ready">
  <img src="https://img.shields.io/badge/License-MIT-blue" alt="MIT License">
</p>

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


## Why Use This API Server?

This API server offers a powerful, scalable, and cost-effective alternative to relying on hosted text embedding APIs like OpenAI’s embedding service. 
Here are the key benefits:

#### 1. Overcome Rate Limits and Latency Bottlenecks
- Hosted APIs have strict rate limits that can throttle throughput.
- This server uses Ray Serve autoscaling to handle **high concurrency** and **large request volumes** without external API restrictions.
- Embeddings are generated locally or in your cloud environment, reducing latency.

#### 2. Cost-Effective at Scale
- Hosted embedding APIs charge per request, which can get expensive with millions of calls.
- Running your own embedding model (e.g., `intfloat/multilingual-e5-base`) on GPUs reduces costs.
- Autoscaling helps optimize resource usage and spending.

#### 3. Greater Control and Customization
- Choose and update your embedding model anytime without waiting for third-party API updates.
- Customize preprocessing or postprocessing as needed.
- Integrate seamlessly with monitoring tools like Prometheus, Grafana, and Ray Dashboard.

#### 4. Privacy and Data Security
- Keep sensitive or proprietary text in your own environment.
- Avoid sending data to third-party services, ensuring better compliance and data protection.

By deploying this API server, you gain full control, scalability, and cost efficiency—making it ideal for production workloads requiring high-throughput semantic embeddings.


## Table of Contents

* [Installation](#installation)
* [Running the Server](#running-the-server)
* [API Usage](#api-usage)
* [Testing](#testing)
* [Monitoring & Observability](#monitoring--observability)
* [Docker & Deployment](#docker--deployment)
* [Repository Structure](#repository-structure)
* [Troubleshooting](#troubleshooting)
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

**Example:**

```bash
curl -X GET "http://localhost:8000/health"
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

- ** Ray Serve Dashboard:** [http://localhost:8265](http://localhost:8265)  
  Track replica scaling, request queues, latency, errors, and resource utilization.

- ** Prometheus Dashboard:** [http://localhost:9090](http://localhost:9090)  
  Explore raw metrics and PromQL queries.

- ** Grafana Dashboard:** [http://localhost:3000](http://localhost:3000)  
  Visual dashboards for Requests Per Minute (RPM), QPS, Latency (P95, P99), Error Rates, CPU/GPU Utilization


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
e5-embedding-ray-serve/
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

## Troubleshooting

You would need **NVIDIA Container Toolkit** installed to enable Docker to use the GPU. 
You may also need to update the default runtime in `/etc/docker/daemon.json` with
```json
{
    "default-runtime": "nvidia",
    "runtimes": {
        "nvidia": {
            "args": [],
            "path": "/usr/bin/nvidia-container-runtime"
        }
    }
}
```
and then restart Docker service.
```bash
sudo systemctl restart docker
```

You may configure the GPU allocation by adding or removing the following code segments:

In `docker-compose.yml`:
```
services:
  ray-embed-server:
    ...
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]
```

In `app/serve_app.py`, by updating `ray_actor_options={"num_gpus": 1}`.


## License

This project is licensed under the MIT License.
