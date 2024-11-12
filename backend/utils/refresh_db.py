import pandas as pd
from s3_utils import list_s3_bucket_items, get_s3_object_metadata
import csv
from tqdm import tqdm

# Function to update CSV with model and prompt derived from object_name
def update_csv(csv_fpath, bucket_name="text2videoviewer"):
    all_objects = list_s3_bucket_items(bucket_name)  # List of object names in the bucket
    records = []
    
    for obj in all_objects:
        # Split the object name into model and prompt using the provided pattern
        parts = obj.rsplit("/", 1)
        if len(parts) != 2:
            continue  # Skip if the object name doesn't match the expected pattern
        
        model = parts[0]  # model is before the "/"
        prompt_with_extension = parts[1]  # prompt with the ".mp4" extension
        
        # Remove the file extension (.mp4) to extract the prompt
        if prompt_with_extension.endswith(".mp4"):
            prompt = prompt_with_extension[:-4]  # Remove the ".mp4" extension
        else:
            continue  # Skip if the object name doesn't end with .mp4

        records.append({
            "model": model, 
            "prompt": prompt, 
            "object_name": obj
        })

    # Create DataFrame
    df = pd.DataFrame(records)
    print(f"Found a total of {len(records)} videos in S3.")

    # Filter models
    df = filter_records_based_on_model(df)

    # Filter prompts based on prompts.csv
    df = filter_records_based_on_prompts(df, "prompts.csv")

    # Print number of prompts filtered out and number of prompts kept
    print(f"Kept {len(df)} videos.")

    # Update name "opensora" to "opensora-v1.2"
    df["model"] = df["model"].replace({"opensora": "opensora-v1.2"})

    # Add base_prompt metadata after filtering
    df = add_base_prompt_metadata(df, bucket_name)

    df.to_csv(csv_fpath, index=False, quoting=csv.QUOTE_ALL, encoding='utf-8')

# Function to filter DataFrame based on records in prompts.csv
def filter_records_based_on_prompts(df, prompts_csv_fpath):
    prompts_df = pd.read_csv(prompts_csv_fpath)
    filtered_df = df[df["prompt"].isin(prompts_df["prompt"])]

    # Print information about kept and excluded prompts
    for model in filtered_df["model"].unique():
        print(f"Kept prompts for model {model} ({len(filtered_df[filtered_df['model'] == model]['prompt'].unique())} videos):")
        for prompt in filtered_df[filtered_df["model"] == model]["prompt"].unique():
            print(f"\t{prompt}")
        
        excluded_prompts = set(prompts_df["prompt"]) - set(filtered_df[filtered_df["model"] == model]["prompt"].unique())
        print(f"Excluded prompts for model {model} ({len(excluded_prompts)} prompts):")
        for prompt in excluded_prompts:
            print(f"\t{prompt}")
    
    return filtered_df

# Function to filter DataFrame based on model
def filter_records_based_on_model(df, sota_models=["cog", "pyramidflow", "opensora", "mochi"]):
    filtered_df = df[df["model"].isin(sota_models)]
    
    # Print filtering result for models
    print(f"Filtered to {len(filtered_df)} records from the following SOTA models: {', '.join(sota_models)}.")
    
    return filtered_df


# Function to add base_prompt metadata to the DataFrame
def add_base_prompt_metadata(df, bucket_name):
    base_prompts = []
    
    # Iterate over the DataFrame rows with a progress bar
    for index, row in tqdm(df.iterrows(), total=len(df), desc="Fetching Metadata", unit="object"):
        object_name = row["object_name"]
        
        # Get metadata for the object
        metadata = get_s3_object_metadata(bucket_name, object_name)
        
        # Extract base_prompt from metadata (assuming it's part of the metadata)
        base_prompt = metadata.get("base_prompt", "")
        base_prompts.append(base_prompt)
    
    # Add base_prompt as a new column in the DataFrame
    df["base_prompt"] = base_prompts
    print("Added base_prompt metadata to DataFrame.")
    
    return df


if __name__ == "__main__":

    csv_fpath = "/home/ubuntu/text2vid-viewer/frontend/db.csv"
    update_csv(csv_fpath)
