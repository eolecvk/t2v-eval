#!/bin/bash

MODEL="all" # Set default value for MODEL
ROOT_DIR="/home/ubuntu"
ENV_PATH="/home/ubuntu/text2vid-viewer/.env"
PROMPT_TXT_PATH="/home/ubuntu/text2vid-viewer/prompts.txt"
PROMPT_CSV_PATH="/home/ubuntu/text2vid-viewer/prompts.csv"

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

# Model argument validation
if [ "$MODEL" != "all" ] && [ ! -d "/home/ubuntu/text2vid-viewer/backend/models/$MODEL" ]; then
    echo "Model not found: $MODEL"
    echo "Available models: $(ls /home/ubuntu/text2vid-viewer/backend/models)"
    exit 1
fi

echo "Model set to: $MODEL"

# Function to run inference for a single model (and export to S3)
run_inference() {
    MODEL="$1"
    echo "Running inference for model: $MODEL"
    DEPLOY_SCRIPT="/home/ubuntu/text2vid-viewer/backend/models/$MODEL/deploy.sh"
    /bin/bash "${DEPLOY_SCRIPT}" || { echo "Failed to run inference for model: $MODEL"; exit 1; }
    python /home/ubuntu/text2vid-viewer/backend/utils/s3_export.py --model "$MODEL" --prompt_csv "$PROMPT_CSV_PATH" || { echo "Failed to export videos to S3"; exit 1; }
    echo "Completed inference for model: $MODEL"
    echo "-----------------------------------"
    echo ""
}

# Load environment variables from the .env file
if [ -f $ENV_PATH ]; then
    source $ENV_PATH
else
    echo "file not found: $ENV_PATH"
    exit 1
fi

cd "$ROOT_DIR"

# Throw error if prompts.csv and prompts.txt do not exist
if [ ! -f "$PROMPT_CSV_PATH" ]; then 
    echo "Prompt file not found at ${PROMPT_CSV_PATH}"
    exit 1
fi

# Create prompts.txt from prompts.csv
echo "Preprocessing prompts..."
python /home/ubuntu/text2vid-viewer/backend/utils/validate_prompts.py --prompt_path "$PROMPT_CSV_PATH" || { echo "Invalid prompts"; exit 1; }

# Install backend dependencies (that are common across models)
if ! command -v pip &> /dev/null; then
    echo "Pip not found. Installing pip"
    sudo apt-get update
    sudo apt-get install python3-pip -y || { echo "Failed to install pip"; exit 1; }
fi

echo "Installing dependencies..."
pip install boto3 python-dotenv pandas || { echo "Failed to install dependencies"; exit 1; }

# Create log and data directories owned by ubuntu
mkdir -p /home/ubuntu/logs /home/ubuntu/data

if [ "$MODEL" == "all" ]; then
    echo "Running inference for all models..."
    for model in $(ls -d /home/ubuntu/text2vid-viewer/backend/models/*/ | xargs -n 1 basename); do
        mkdir -p /home/ubuntu/data/"$model"
        run_inference "$model"
    done
else
    run_inference "$MODEL"
fi

echo "Completed run_inference.sh"
# Tune OpenSora sampling rate for smoother motion [2024-08-29T12:11:00]

# Fix CogVideo FPS output issue [2024-09-01T10:39:00]

# Fix PyramidFlow memory leak on long prompts [2024-09-04T14:19:00]

# Refactor model dispatch logic in run_inference.sh [2024-09-07T17:40:00]

# Automate metadata generation for S3 uploads [2024-09-09T12:58:00]

# Refactor frontend JS for modularity [2024-09-11T10:11:00]

# Test frontend layout on smaller resolutions [2024-09-14T18:27:00]

# Add notes on EC2 setup for deployment [2024-09-17T16:11:00]

# Add cinematic scene prompts for realism comparison [2024-09-20T09:00:00]

# Fix bash permission on run_inference.sh [2024-09-23T09:03:00]

# Tune OpenSora sampling rate for smoother motion [2024-09-24T11:11:00]

# Fix CogVideo FPS output issue [2024-09-26T13:36:00]

# Fix PyramidFlow memory leak on long prompts [2024-09-29T10:09:00]

# Refactor model dispatch logic in run_inference.sh [2024-10-03T10:36:00]

# Automate metadata generation for S3 uploads [2024-10-06T11:13:00]

# Refactor frontend JS for modularity [2024-10-10T17:37:00]

# Test frontend layout on smaller resolutions [2024-10-12T10:40:00]

# Add notes on EC2 setup for deployment [2024-10-17T12:44:00]

# Add cinematic scene prompts for realism comparison [2024-10-19T10:37:00]

# Fix bash permission on run_inference.sh [2024-10-21T15:28:00]

# Tune OpenSora sampling rate for smoother motion [2024-10-22T09:59:00]

# Fix CogVideo FPS output issue [2024-10-25T15:51:00]

# Fix PyramidFlow memory leak on long prompts [2024-10-27T16:03:00]
