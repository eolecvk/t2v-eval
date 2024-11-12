import torch
from PIL import Image
from pyramid_dit import PyramidDiTForVideoGeneration
from diffusers.utils import load_image, export_to_video

def load_prompts(prompt_path, start_idx=None, end_idx=None):
    with open(prompt_path, "r") as f:
        prompts = [line.strip() for line in f.readlines()]
    if start_idx is not None and end_idx is not None:
        return prompts[start_idx:end_idx]
    return prompts

def dl_model():
    from huggingface_hub import snapshot_download
    model_path = '/home/ubuntu/text2vid-viewer/backend/models/pyramidflow/'   # The local directory to save downloaded checkpoint
    snapshot_download("rain1011/pyramid-flow-sd3", local_dir=model_path, local_dir_use_symlinks=False, repo_type='model')


def run_inference(prompts):
    torch.cuda.set_device(0)
    model_dtype, torch_dtype = 'bf16', torch.bfloat16   # Use bf16 (not support fp16 yet)

    MODEL_PATH = "/home/ubuntu/text2vid-viewer/backend/models/pyramidflow/"
    model = PyramidDiTForVideoGeneration(
        MODEL_PATH,
        model_dtype,
        model_variant='diffusion_transformer_768p',     # 'diffusion_transformer_384p'
    )

    model.vae.to("cuda")
    model.dit.to("cuda")
    model.text_encoder.to("cuda")
    model.vae.enable_tiling()


    for prompt_i, prompt in enumerate(prompts):

        print("Prompt:", prompt)

        with torch.no_grad(), torch.cuda.amp.autocast(enabled=True, dtype=torch_dtype):
            frames = model.generate(
                prompt=prompt,
                num_inference_steps=[20, 20, 20],
                video_num_inference_steps=[10, 10, 10],
                height=768,     
                width=1280,
                temp=16,                    # temp=16: 5s, temp=31: 10s
                guidance_scale=9.0,         # The guidance for the first frame, set it to 7 for 384p variant
                video_guidance_scale=5.0,   # The guidance for the other video latent
                output_type="pil",
                save_memory=True,           # If you have enough GPU memory, set it to `False` to improve vae decoding speed
            )

        export_to_video(frames, f"/home/ubuntu/data/pyramidflow/sample_{prompt_i}.mp4", fps=24)

        

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt_path", type=str, default=None)
    prompt_path = parser.parse_args().prompt_path

    prompts = load_prompts(prompt_path)

    dl_model()
    run_inference(prompts)