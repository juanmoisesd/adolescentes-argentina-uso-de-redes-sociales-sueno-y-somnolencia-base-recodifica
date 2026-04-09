#!/bin/bash
set -e
for i in {1..10}; do
    script=$(ls phase_${i}_*.py)
    echo "Running $script..."
    python3 "$script"
done
echo "Full Pipeline Success!"
