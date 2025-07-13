#!/bin/bash
ray start --head --port=6379 --dashboard-host=0.0.0.0 --metrics-export-port=8080 &
sleep 5
python serve_app.py