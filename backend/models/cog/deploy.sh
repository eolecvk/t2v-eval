cd /home/ubuntu
git clone https://github.com/THUDM/CogVideo.git
cd CogVideo
pip install -r requirements.txt

# Patch the inference script
cp /home/ubuntu/text2vid-viewer/backend/models/cog/inference.py /home/ubuntu/CogVideo/inference/inference.py

# Run inference
python /home/ubuntu/CogVideo/inference/inference.py \
    --prompt_path /home/ubuntu/text2vid-viewer/prompts.txt \
    --save_dir /home/ubuntu/data/cog \
    --model_path THUDM/CogVideoX-5b \
    --generate_type "t2v"