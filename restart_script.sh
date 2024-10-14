#!/bin/bash
#Kill any running instance of the Python script
pkill -f chatbot/main.py

# Start the script again
cd /app && export PYTHONPATH=/app && /usr/local/bin/python chatbot/main.py