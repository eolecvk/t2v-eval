#!/bin/bash

MODEL="opensora-v1-2-720p"

# Parse arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --model)
            MODEL="$2"
            shift # past argument
            shift # past value
            ;;
        *)
            echo "Unknown argument: $1"
            exit 1
            ;;
    esac
done

echo "Using model: $MODEL"

# Load environment variables from the .env file
ENV_PATH="/home/ubuntu/text2vid-viewer/.env"
if [ -f $ENV_PATH ]; then
    export $(cat $ENV_PATH | xargs)
else
    echo "file not found: $ENV_PATH"
    exit 1
fi

# Variables
OPEN_SORA_REPO="https://github.com/hpcaitech/Open-Sora.git"
IMAGE_EVAL_REPO="https://github.com/LambdaLabsML/text2vid-viewer.git"
OPEN_SORA_DIR="Open-Sora"

# Function to handle errors
handle_error() {
    echo "Error occurred in script at line: $1"
    exit 1
}

# Trap errors
trap 'handle_error $LINENO' ERR

# Remove all containers
containers=$(sudo docker ps -qa)
if [ -n "$containers" ]; then
    echo "Removing all existing containers..."
    sudo docker rm -v -f $containers
else
    echo "No containers to remove"
fi

# Clone OpenSora repository if not exists
if [ ! -d "$OPEN_SORA_DIR" ]; then
    git clone --quiet $OPEN_SORA_REPO > /dev/null || { echo "Failed to clone OpenSora repository"; exit 1; }
else
    echo "Open-Sora directory already exists. Skipping clone."
fi

# Build the opensora-inference image
echo "Building opensora-inference Docker image..."
cd /home/ubuntu/text2vid-viewer
sudo docker build --no-cache -t opensora-inference -f backend/models/opensora/Dockerfile . || { echo "Failed to build opensora-inference Docker image"; exit 1; }

# Run container opensora-inference
# Ensure any container with same name is removed first
echo "Running opensora-inference container..."
if sudo docker ps -a --format '{{.Names}}' | grep -Eq "^opensora-inference$"; then
    sudo docker rm -f opensora-inference || { echo "Failed to remove existing opensora-inference Docker container"; exit 1; }
fi

# Run the inference
sudo docker run \
    --rm \
    --gpus all \
    --env-file /home/ubuntu/text2vid-viewer/.env \
    -v /home/ubuntu/data/opensora:/data \
    -v /home/ubuntu/logs:/app/logs \
    --name opensora_inference \
    opensora-inference:latest \
    --model ${MODEL}