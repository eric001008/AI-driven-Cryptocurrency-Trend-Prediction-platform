#!/bin/bash

echo "Starting data analysis loop..."

# Optional: Load environment variables (if main.py does not have load_dotenv)
# source /app/.env

while true
do
    echo " Running Analysis at $(date)"
    python /app/analysis.py
    sleep  60
done
