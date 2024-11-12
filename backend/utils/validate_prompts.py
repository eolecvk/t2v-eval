import sys
import os
import pandas as pd
import csv

def process_prompts(file_path):
    # Read CSV into a DataFrame
    try:
        df = pd.read_csv(file_path).fillna("")
    except Exception as e:
        raise RuntimeError(f"Error loading CSV file: {e}")

    # Ensure required columns are present
    if 'prompt' not in df.columns or 'base_prompt' not in df.columns:
        raise ValueError("CSV must have 'prompt' and 'base_prompt' columns.")

    # Check for non-compliance (empty prompt, length > 650, or containing forward slash)
    if df['prompt'].eq("").any() or df['prompt'].str.len().gt(650).any():
        raise ValueError("Error: Prompts cannot be empty and must be 650 characters or less.")
    
    #check if contaning forward slash
    if df['prompt'].str.contains('/').any():
        raise ValueError("Error: Prompts cannot contain forward slash.")

    # Step 6: Save 'prompt' column to prompts.txt
    prompt_txt_path = os.path.join(os.path.dirname(file_path), 'prompts.txt')
    df['prompt'].to_csv(prompt_txt_path, index=False, header=False, quoting=csv.QUOTE_ALL)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Process prompts from a CSV file")
    parser.add_argument("--prompt_path", type=str, default="/home/ubuntu/text2vid-viewer/prompts.csv", help="Path to the prompt CSV file")
    prompt_path = parser.parse_args().prompt_path

    try:
        process_prompts(prompt_path)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
