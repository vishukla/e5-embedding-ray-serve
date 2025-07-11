#!/bin/bash
ray start --head --port=6379 --dashboard-host=0.0.0.0 &
sleep 5
python serve_app.py