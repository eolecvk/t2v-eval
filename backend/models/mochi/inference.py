import json
import os
import tempfile
import time

import click
import numpy as np
import ray
from einops import rearrange
from PIL import Image
from tqdm import tqdm
import torch

from mochi_preview.handler import MochiWrapper

model = None
model_path = None


def set_model_path(path):
    global model_path
    model_path = path


def load_model():
    global model, model_path
    if model is None:
        ray.init()
        MOCHI_DIR = model_path
        VAE_CHECKPOINT_PATH = f"{MOCHI_DIR}/vae.safetensors"
        MODEL_CONFIG_PATH = f"{MOCHI_DIR}/dit-config.yaml"
        MODEL_CHECKPOINT_PATH = f"{MOCHI_DIR}/dit.safetensors"
        num_gpus = torch.cuda.device_count()
        if num_gpus < 4:
            print(f"WARNING: Mochi requires at least 4xH100 GPUs, but only {num_gpus} GPU(s) are available.")
        print(f"Launching with {num_gpus} GPUs.")

        model = MochiWrapper(
            num_workers=num_gpus,
            vae_stats_path=f"{MOCHI_DIR}/vae_stats.json",
            vae_checkpoint_path=VAE_CHECKPOINT_PATH,
            dit_config_path=MODEL_CONFIG_PATH,
            dit_checkpoint_path=MODEL_CHECKPOINT_PATH,
        )

def linear_quadratic_schedule(num_steps, threshold_noise, linear_steps=None):
    if linear_steps is None:
        linear_steps = num_steps // 2
    linear_sigma_schedule = [i * threshold_noise / linear_steps for i in range(linear_steps)]
    threshold_noise_step_diff = linear_steps - threshold_noise * num_steps
    quadratic_steps = num_steps - linear_steps
    quadratic_coef = threshold_noise_step_diff / (linear_steps * quadratic_steps ** 2)
    linear_coef = threshold_noise / linear_steps - 2 * threshold_noise_step_diff / (quadratic_steps ** 2)
    const = quadratic_coef * (linear_steps ** 2)
    quadratic_sigma_schedule = [
        quadratic_coef * (i ** 2) + linear_coef * i + const
        for i in range(linear_steps, num_steps)
    ]
    sigma_schedule = linear_sigma_schedule + quadratic_sigma_schedule + [1.0]
    sigma_schedule = [1.0 - x for x in sigma_schedule]
    return sigma_schedule

def generate_video(
    prompt,
    save_dir,
    prompt_idx,
    negative_prompt,
    width,
    height,
    num_frames,
    seed,
    cfg_scale,
    num_inference_steps,
):
    #load_model()

    # sigma_schedule should be a list of floats of length (num_inference_steps + 1),
    # such that sigma_schedule[0] == 1.0 and sigma_schedule[-1] == 0.0 and monotonically decreasing.
    sigma_schedule = linear_quadratic_schedule(num_inference_steps, 0.025)

    # cfg_schedule should be a list of floats of length num_inference_steps.
    # For simplicity, we just use the same cfg scale at all timesteps,
    # but more optimal schedules may use varying cfg, e.g:
    # [5.0] * (num_inference_steps // 2) + [4.5] * (num_inference_steps // 2)
    cfg_schedule = [cfg_scale] * num_inference_steps

    args = {
        "height": height,
        "width": width,
        "num_frames": num_frames,
        "mochi_args": {
            "sigma_schedule": sigma_schedule,
            "cfg_schedule": cfg_schedule,
            "num_inference_steps": num_inference_steps,
            "batch_cfg": True,
        },
        "prompt": [prompt],
        "negative_prompt": [negative_prompt],
        "seed": seed,
    }

    final_frames = None
    for cur_progress, frames, finished in tqdm(model(args), total=num_inference_steps + 1):
        final_frames = frames

    assert isinstance(final_frames, np.ndarray)
    assert final_frames.dtype == np.float32

    final_frames = rearrange(final_frames, "t b h w c -> b t h w c")
    final_frames = final_frames[0]

    os.makedirs(save_dir, exist_ok=True)
    output_path = os.path.join(save_dir, f"sample_{prompt_idx}.mp4")

    with tempfile.TemporaryDirectory() as tmpdir:
        frame_paths = []
        for i, frame in enumerate(final_frames):
            frame = (frame * 255).astype(np.uint8)
            frame_img = Image.fromarray(frame)
            frame_path = os.path.join(tmpdir, f"frame_{i:04d}.png")
            frame_img.save(frame_path)
            frame_paths.append(frame_path)

        frame_pattern = os.path.join(tmpdir, "frame_%04d.png")
        ffmpeg_cmd = f"ffmpeg -y -r 30 -i {frame_pattern} -vcodec libx264 -pix_fmt yuv420p {output_path}"
        os.system(ffmpeg_cmd)

        json_path = os.path.splitext(output_path)[0] + ".json"
        with open(json_path, "w") as f:
            json.dump(args, f, indent=4)

    return output_path

def generate_videos(
    prompts,
    negative_prompt,
    width,
    height,
    num_frames,
    seed,
    cfg_scale,
    num_inference_steps,
):
    #load_model()
    for prompt in prompts:
    
        # sigma_schedule should be a list of floats of length (num_inference_steps + 1),
        # such that sigma_schedule[0] == 1.0 and sigma_schedule[-1] == 0.0 and monotonically decreasing.
        sigma_schedule = linear_quadratic_schedule(num_inference_steps, 0.025)

        # cfg_schedule should be a list of floats of length num_inference_steps.
        # For simplicity, we just use the same cfg scale at all timesteps,
        # but more optimal schedules may use varying cfg, e.g:
        # [5.0] * (num_inference_steps // 2) + [4.5] * (num_inference_steps // 2)
        cfg_schedule = [cfg_scale] * num_inference_steps

        args = {
            "height": height,
            "width": width,
            "num_frames": num_frames,
            "mochi_args": {
                "sigma_schedule": sigma_schedule,
                "cfg_schedule": cfg_schedule,
                "num_inference_steps": num_inference_steps,
                "batch_cfg": True,
            },
            "prompt": [prompt],
            "negative_prompt": [negative_prompt],
            "seed": seed,
        }

        final_frames = None
        for cur_progress, frames, finished in tqdm(model(args), total=num_inference_steps + 1):
            final_frames = frames

        assert isinstance(final_frames, np.ndarray)
        assert final_frames.dtype == np.float32

        final_frames = rearrange(final_frames, "t b h w c -> b t h w c")
        final_frames = final_frames[0]

        os.makedirs("outputs", exist_ok=True)
        output_path = os.path.join("outputs", f"output_{int(time.time())}.mp4")

        with tempfile.TemporaryDirectory() as tmpdir:
            frame_paths = []
            for i, frame in enumerate(final_frames):
                frame = (frame * 255).astype(np.uint8)
                frame_img = Image.fromarray(frame)
                frame_path = os.path.join(tmpdir, f"frame_{i:04d}.png")
                frame_img.save(frame_path)
                frame_paths.append(frame_path)

            frame_pattern = os.path.join(tmpdir, "frame_%04d.png")
            ffmpeg_cmd = f"ffmpeg -y -r 30 -i {frame_pattern} -vcodec libx264 -pix_fmt yuv420p {output_path}"
            os.system(ffmpeg_cmd)

            json_path = os.path.splitext(output_path)[0] + ".json"
            with open(json_path, "w") as f:
                json.dump(args, f, indent=4)

    return output_path



def load_prompts(prompt_path, start_idx=None, end_idx=None):
    with open(prompt_path, "r") as f:
        prompts = [line.strip() for line in f.readlines()]
    if start_idx is not None and end_idx is not None:
        return prompts[start_idx:end_idx]
    return prompts

@click.command()
@click.option("--prompt_path", required=False, help="Prompt for video generation.")
@click.option("--model_path", required=True, help="Path to the model directory.")
@click.option("--save_dir", required=True, help="Path to save the generated videos")
@click.option("--prompt", required=False, help="Prompt for video generation.")
@click.option(
    "--negative_prompt", default="", help="Negative prompt for video generation."
)
@click.option("--width", default=848, type=int, help="Width of the video.")
@click.option("--height", default=480, type=int, help="Height of the video.")
@click.option("--num_frames", default=163, type=int, help="Number of frames.")
@click.option("--seed", default=12345, type=int, help="Random seed.")
@click.option("--cfg_scale", default=4.5, type=float, help="CFG Scale.")
@click.option(
    "--num_steps", default=64, type=int, help="Number of inference steps."
)
def generate_cli(
    prompt_path,
    model_path,
    save_dir,
    prompt,
    negative_prompt,
    width,
    height,
    num_frames,
    seed,
    cfg_scale,
    num_steps,
):
    prompts = load_prompts(prompt_path)
    set_model_path(model_path)
    load_model()

    for prompt_idx, prompt in enumerate(prompts):

        output = generate_video(
            prompt,
            save_dir,
            prompt_idx,
            negative_prompt,
            width,
            height,
            num_frames,
            seed,
            cfg_scale,
            num_steps,
        )
        click.echo(f"Video generated at: {output}")




if __name__ == "__main__":
    generate_cli()