#!/bin/bash

# Check that .env file exists
if [ ! -f .env ]; then
    echo ".env file not found in dir root!"
    exit 1
fi

# Source the .env file
export $(grep -v '^#' .env | xargs)
echo "Sourced .env file"

# Make sure pip and venv are installed
if ! command -v pip &> /dev/null; then
    echo "Pip not found. Installing pip"
    sudo apt-get update
    sudo apt-get install python3-pip python3-venv -y || { echo "Failed to install pip or venv"; exit 1; }
fi

# Create a virtual environment if not already created
if [ ! -d "venv" ]; then
    python3 -m venv venv || { echo "Failed to create virtual environment"; exit 1; }
    echo "Created virtual environment"
fi

# Install pip manually if not present in the virtual environment
if [ ! -f "venv/bin/pip" ]; then
    echo "Pip not found in virtual environment. Installing pip manually."
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py || { echo "Failed to download get-pip.py"; exit 1; }
    venv/bin/python3 get-pip.py || { echo "Failed to install pip manually in virtual environment"; exit 1; }
    rm get-pip.py
fi

# Upgrade pip inside the virtual environment
venv/bin/python3 -m pip install --upgrade pip || { echo "Failed to upgrade pip"; exit 1; }


# Install dependencies in the virtual environment
venv/bin/python3 -m pip install flatbuffers boto3 python-dotenv pandas tqdm || { echo "Failed to install dependencies"; exit 1; }
echo "Installed dependencies"

# Refresh db.csv
venv/bin/python3 backend/utils/refresh_db.py || { echo "Failed to refresh db.csv"; exit 1; }
echo "Refreshed db.csv"

# Run frontend server
echo "Running frontend server"
cd frontend
../venv/bin/python3 -m http.server 8000

# Fix bug in OpenSora video resolution config [2024-08-29T09:41:00]

# Update CogVideo prompts for diversity [2024-09-02T15:26:00]

# Update PyramidFlow decoder checkpoint [2024-09-04T18:38:00]

# Log GPU memory usage for each model [2024-09-07T14:16:00]

# Add S3 upload retry logic for robustness [2024-09-09T09:30:00]

# Improve CSS for mobile responsiveness [2024-09-11T17:34:00]

# Fix mismatch in prompt label rendering [2024-09-14T18:19:00]

# Fix typo in installation instructions [2024-09-17T09:37:00]
