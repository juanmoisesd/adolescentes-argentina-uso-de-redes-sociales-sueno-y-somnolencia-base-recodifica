#!/bin/bash
set -e

echo "Starting data validation..."
make validate

echo "Running tests..."
pytest tests/

echo "Processing data..."
# python scripts/etl/process.py

echo "Analysis complete."
