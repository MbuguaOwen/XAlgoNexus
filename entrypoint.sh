#!/bin/sh

set -e  # Exit on error

echo "[XALGO] Starting live controller..."
exec python src/main/live_controller.py
