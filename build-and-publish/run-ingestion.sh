#!/bin/bash
# Wrapper script to run ingestion with OMP_NUM_THREADS set

set -eo pipefail

# Set OMP_NUM_THREADS to avoid PyTorch OpenMP memory allocation issues
export OMP_NUM_THREADS=1

# Run the ingestion script
.venv/bin/python -m src.ingestion.main
