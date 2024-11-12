cd /home/ubuntu
git clone https://github.com/genmoai/models mochi
cd mochi 
pip install uv

uv venv .venv
source .venv/bin/activate
uv pip install setuptools torch==2.4.1 huggingface_hub[cli] python-dotenv
uv pip install -e . --no-build-isolation

# Patch the inference script
cp /home/ubuntu/text2vid-viewer/backend/models/mochi/inference.py /home/ubuntu/mochi/src/mochi_preview/inference.py

# Download model weights
MODEL_PATH=/home/ubuntu/text2vid-viewer/backend/models/mochi/weights
python3 /home/ubuntu/text2vid-viewer/backend/models/mochi/dl_weights.py --model_path $MODEL_PATH

# Run inference
python3 /home/ubuntu/mochi/src/mochi_preview/inference.py \
    --prompt_path /home/ubuntu/text2vid-viewer/prompts.txt \
    --save_dir /home/ubuntu/data/mochi \
    --model_path $MODEL_PATH