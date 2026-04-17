#!/bin/bash
cd /Users/mdrabbyhasan/atm-fraud-detection-system/backend
export PYTHONPATH="/Users/mdrabbyhasan/atm-fraud-detection-system/backend/venv/lib/python3.12/site-packages:/Users/mdrabbyhasan/atm-fraud-detection-system/backend"
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000