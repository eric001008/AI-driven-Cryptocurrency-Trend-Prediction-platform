#!/bin/bash

echo "Starting all acquisition loops..."


while true; do
    echo "Fetch coin data at $(date)"
    python /app/coin_data.py
    sleep 60
done &

# Execute every 15 minutes
while true; do
    echo "Fetch social media data at $(date)"
    python /app/social_data.py
    sleep 900
done &

# Execute every 4 hours
while true; do
    echo "Fetch trading records at $(date)"
    python /app/trading.py
    sleep 14400
done &


# Preventing the script from exiting prematurely
wait
