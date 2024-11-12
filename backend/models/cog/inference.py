import argparse
import os
import re
from typing import List, Literal, Optional

import torch
from diffusers import (
    CogVideoXDDIMScheduler,
    CogVideoXDPMScheduler,
    CogVideoXImageToVideoPipeline,
    CogVideoXPipeline,
    CogVideoXVideoToVideoPipeline,
)
from diffusers.utils import export_to_video, load_image, load_video


def generate_video(
    prompt: str,
    pipe,
    output_path: str = "./output.mp4",
    image: Optional[torch.Tensor] = None,
    video: Optional[torch.Tensor] = None,
    num_inference_steps: int = 50,
    guidance_scale: float = 6.0,
    num_videos_per_prompt: int = 1,
    seed: int = 42,
):
    """
    Generates a video based on the given prompt and saves it to the specified path.

    Parameters:
    - prompt (str): The description of the video to be generated.
    - pipe: The pre-initialized pipeline object.
    - output_path (str): The path where the generated video will be saved.
    - image (Optional[torch.Tensor]): The image tensor for image-to-video generation.
    - video (Optional[torch.Tensor]): The video tensor for video-to-video generation.
    - num_inference_steps (int): Number of steps for the inference process. More steps can result in better quality.
    - guidance_scale (float): The scale for classifier-free guidance. Higher values can lead to better alignment with the prompt.
    - num_videos_per_prompt (int): Number of videos to generate per prompt.
    - seed (int): The seed for reproducibility.
    """

    # Generate the video frames based on the prompt.
    if image is not None:
        video_generate = pipe(
            prompt=prompt,
            image=image,
            num_videos_per_prompt=num_videos_per_prompt,
            num_inference_steps=num_inference_steps,
            num_frames=49,
            use_dynamic_cfg=True,
            guidance_scale=guidance_scale,
            generator=torch.Generator().manual_seed(seed),
        ).frames[0]
    elif video is not None:
        video_generate = pipe(
            prompt=prompt,
            video=video,
            num_videos_per_prompt=num_videos_per_prompt,
            num_inference_steps=num_inference_steps,
            # num_frames=49,
            use_dynamic_cfg=True,
            guidance_scale=guidance_scale,
            generator=torch.Generator().manual_seed(seed),
        ).frames[0]
    else:
        video_generate = pipe(
            prompt=prompt,
            num_videos_per_prompt=num_videos_per_prompt,
            num_inference_steps=num_inference_steps,
            num_frames=49,
            use_dynamic_cfg=True,
            guidance_scale=guidance_scale,
            generator=torch.Generator().manual_seed(seed),
        ).frames[0]

    # Export the generated frames to a video file. fps must be 8 for original video.
    export_to_video(video_generate, output_path, fps=8)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate videos from text prompts using CogVideoX")
    parser.add_argument("--prompt", type=str, required=False, help="The description of the video to be generated")
    parser.add_argument("--prompt_path", type=str, help="Path to a text file containing prompts (one per line)")
    parser.add_argument("--save_dir", type=str, default="./", help="Directory where the generated videos will be saved")
    parser.add_argument(
        "--image_or_video_path",
        type=str,
        default=None,
        help="The path of the image or video to be used as the background",
    )
    parser.add_argument(
        "--model_path", type=str, default="THUDM/CogVideoX-5b", help="The path of the pre-trained model to be used"
    )
    parser.add_argument("--lora_path", type=str, default=None, help="The path of the LoRA weights to be used")
    parser.add_argument("--lora_rank", type=int, default=128, help="The rank of the LoRA weights")
    parser.add_argument(
        "--output_path", type=str, default=None, help="The path where the generated video will be saved"
    )
    parser.add_argument("--guidance_scale", type=float, default=6.0, help="The scale for classifier-free guidance")
    parser.add_argument(
        "--num_inference_steps", type=int, default=50, help="Number of steps for the inference process"
    )
    parser.add_argument("--num_videos_per_prompt", type=int, default=1, help="Number of videos to generate per prompt")
    parser.add_argument(
        "--generate_type",
        type=str,
        choices=["t2v", "i2v", "v2v"],
        default="t2v",
        help="The type of video generation ('t2v', 'i2v', 'v2v')",
    )
    parser.add_argument(
        "--dtype", type=str, choices=["float16", "bfloat16"], default="bfloat16", help="The data type for computation"
    )
    parser.add_argument("--seed", type=int, default=42, help="The seed for reproducibility")

    args = parser.parse_args()
    dtype = torch.float16 if args.dtype == "float16" else torch.bfloat16

    # Ensure at least one of --prompt or --prompt_path is provided
    if not args.prompt and not args.prompt_path:
        parser.error("At least one of --prompt or --prompt_path must be provided.")

    # Ensure that image_or_video_path is provided for i2v or v2v generation
    if args.generate_type in ["i2v", "v2v"] and not args.image_or_video_path:
        parser.error(f"--image_or_video_path must be provided for generate_type '{args.generate_type}'")

    # Collect prompts
    prompts = []

    if args.prompt:
        prompts.append(args.prompt)

    if args.prompt_path:
        with open(args.prompt_path, 'r') as f:
            prompts.extend([line.strip() for line in f if line.strip()])

    # Create the save directory if it doesn't exist
    os.makedirs(args.save_dir, exist_ok=True)

    # Warn if multiple prompts and output_path is specified
    if len(prompts) > 1 and args.output_path:
        print("Warning: Multiple prompts detected. The '--output_path' argument will be ignored.")

    # Initialize the pipeline once
    if args.generate_type == "i2v":
        pipe = CogVideoXImageToVideoPipeline.from_pretrained(args.model_path, torch_dtype=dtype)
        image = load_image(image=args.image_or_video_path)
        video = None
    elif args.generate_type == "t2v":
        pipe = CogVideoXPipeline.from_pretrained(args.model_path, torch_dtype=dtype)
        image = None
        video = None
    else:  # 'v2v'
        pipe = CogVideoXVideoToVideoPipeline.from_pretrained(args.model_path, torch_dtype=dtype)
        video = load_video(args.image_or_video_path)
        image = None

    # If using LoRA weights
    if args.lora_path:
        pipe.load_lora_weights(
            args.lora_path, weight_name="pytorch_lora_weights.safetensors", adapter_name="test_1"
        )
        pipe.fuse_lora(lora_scale=1 / args.lora_rank)

    # Set Scheduler.
    pipe.scheduler = CogVideoXDPMScheduler.from_config(pipe.scheduler.config, timestep_spacing="trailing")

    # Enable CPU offload for the model.
    pipe.enable_sequential_cpu_offload()

    pipe.vae.enable_slicing()
    pipe.vae.enable_tiling()

    # Loop over prompts and generate videos
    for prompt_i, prompt in enumerate(prompts):
        if len(prompts) == 1 and args.output_path:
            output_path = args.output_path
        else:
            output_path = os.path.join(args.save_dir, f"sample_{prompt_i}.mp4")

        generate_video(
            prompt=prompt,
            pipe=pipe,
            output_path=output_path,
            image=image,
            video=video,
            num_inference_steps=args.num_inference_steps,
            guidance_scale=args.guidance_scale,
            num_videos_per_prompt=args.num_videos_per_prompt,
            seed=args.seed,
        )
