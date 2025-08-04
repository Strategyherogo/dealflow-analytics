#!/bin/bash
# Simple startup script for DigitalOcean App Platform

echo "Starting DealFlow Analytics API..."

# Set default port if not provided
PORT=${PORT:-8000}

# Start the FastAPI application
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1