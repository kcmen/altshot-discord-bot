#!/bin/bash

echo "🔁 Starting AltShot Bot with auto-restart..."

while true
do
  python bot.py
  echo "❌ Bot crashed or exited. Restarting in 1s..."
  sleep 1
done
