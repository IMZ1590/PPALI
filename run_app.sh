#!/bin/bash

# PPALI - Startup Script (V1.0)
# This script starts the backend server using the configured virtual environment.

echo "------------------------------------------------"
echo "Starting PPALI Backend Server..."
echo "------------------------------------------------"

# Change to the backend directory
cd "$(dirname "$0")/backend"

# Start the server using the local virtual environment
/home/minjune/nmr_pca/venv/bin/python3 main.py
