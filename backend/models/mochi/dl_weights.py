import os
from huggingface_hub import snapshot_download

def dl_model(model_path):
    if not os.path.exists(model_path):
        os.makedirs(model_path)
        snapshot_download("genmo/mochi-1-preview", local_dir=model_path, repo_type='model')
    else:
        print(f"Model already exists in the directory: {model_path}")
    


if __name__ == "__main__":

    import argparse
    from dotenv import load_dotenv
    load_dotenv("/home/ubuntu/text2vid-viewer/.env")

    parser = argparse.ArgumentParser(description='Download Mochi model')
    parser.add_argument('--model_path',
        type=str,
        default='/home/ubuntu/text2vid-viewer/backend/models/mochi/weights',
        help='Path to download the model')
    args = parser.parse_args()
    model_path = args.model_path

    dl_model(model_path)