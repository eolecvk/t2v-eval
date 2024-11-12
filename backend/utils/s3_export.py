import argparse
import os
import glob
import pandas as pd
from s3_utils import upload_file_to_s3
from dotenv import load_dotenv

if __name__ == "__main__":

    load_dotenv("/home/ubuntu/text2vid-viewer/.env")
     
    # Parse `model` argument
    parser = argparse.ArgumentParser(description="Send generated videos to S3")
    parser.add_argument("--model", type=str, required=True, help="Name of the model configuration to use")
    parser.add_argument("--prompt_csv", type=str, required=True, help="Path to the prompt csv file")
    
    args = parser.parse_args()
    model = args.model
    prompt_csv = args.prompt_csv

    # Read prompt CSV and create a mapping of prompt to base_prompt
    if not os.path.exists(prompt_csv):
        raise FileNotFoundError(f"Prompt CSV file not found: {prompt_csv}")
    
    df = pd.read_csv(prompt_csv)  # Read CSV with header
    df['base_prompt'] = df['base_prompt'].fillna('')  # Fill NaN values in 'base_prompt' with empty string
    # Assuming CSV contains 'prompt' and 'base_prompt' columns
    prompts = df['prompt'].tolist()  # Get the 'prompt' column
    base_prompts = df['base_prompt'].tolist()  # Get the 'base_prompt' column

    print("prompts")
    print(prompts)
    print()
    print("base_prompts")
    print(base_prompts)
    print()

    # Export to S3
    generated_files = glob.glob(os.path.join(f"/home/ubuntu/data/{model}", '*.mp4'))

    print("generated_files")
    print(generated_files)
    print()
    
    for generated_file_path in generated_files:
        # Extract the index from the file path (e.g., "sample_001.mp4" -> 001)
        filename = os.path.basename(generated_file_path)
        index_str = filename.split('_')[-1].split('.mp4')[0]
        
        try:
            index = int(index_str)  # Convert index string to int (index starts from 0)
        except ValueError:
            print(f"Error: Could not extract valid index from filename: {filename}")
            continue

        if index < 0 or index >= len(prompts):
            print(f"Error: Index {index} out of range for available prompts.")
            continue

        prompt = prompts[index]  # Retrieve the original prompt based on the index
        base_prompt = base_prompts[index]  # Retrieve the corresponding base_prompt
        bucket_name = "text2videoviewer"
        object_name = f"{model}/{prompt}.mp4"  # Corrected the object name

        metadata = {
            "model": model,
            "prompt": prompt,
            "base_prompt": base_prompt  # Include base_prompt in the metadata
        }

        print("SENDING TO S3")
        print(f"prompt: {prompt}")
        print(f"base_prompt: {base_prompt}")
        print(f"bucket_name: {bucket_name}")
        print(f"object_name: {object_name}")
        print()


        response = upload_file_to_s3(generated_file_path, bucket_name, object_name, metadata)
        if response is None:
            print(f"File upload failed for {generated_file_path}.")
