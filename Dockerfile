FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git curl build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY entrypoint.sh .
RUN chmod +x /app/entrypoint.sh

COPY app .
COPY tests/ ./tests/

EXPOSE 8000 8265 6379

CMD ["./entrypoint.sh"]