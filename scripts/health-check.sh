#!/bin/bash
set -e

echo "=== Running AI TradeQ Health Verification ==="

echo "[1/4] Checking Backend API Root Health..."
curl -s -f http://localhost:8000/health || (echo "Backend health failed" && exit 1)

echo "[2/4] Checking API v1 Health & Database Query..."
curl -s -f http://localhost:8000/api/v1/health || (echo "API v1 health failed" && exit 1)

echo "[3/4] Checking Frontend Dev Server (HTTP status)..."
curl -s -f http://localhost:3000 > /dev/null || (echo "Frontend check warning: Ensure frontend server is active.")

echo "[4/4] Health checks completed successfully!"
