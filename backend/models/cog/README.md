git clone https://github.com/THUDM/CogVideo.git
cd CogVideo
pip install -r requirements.txt

cd inference
python inference.py \
    --prompt_path /home/ubuntu/text2vid-viewer/prompts.txt \
    --save_dir /home/ubuntu/data \
    --model_path THUDM/CogVideoX-5b \
    --generate_type "t2v"
