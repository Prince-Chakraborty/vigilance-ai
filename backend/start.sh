#!/bin/bash
export PYTHONPATH=/Users/princechakraborty/vigilance-ai/core
python3 -m uvicorn main:app --reload --port 8000
