#!/bin/bash
# Quick script to run the scraper with virtual environment

cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Run scraper with any arguments passed
python scraper.py "$@"

# Deactivate virtual environment
deactivate

