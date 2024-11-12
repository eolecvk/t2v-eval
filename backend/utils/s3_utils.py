import pandas as pd
import csv
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from dotenv import load_dotenv
import os

def upload_file_to_s3(file_name, bucket_name, object_name, metadata={}):
    """
    Uploads a file to an S3 bucket.

    :param file_name: Path to the file to upload.
    :param bucket_name: Name of the S3 bucket.
    :param object_name: S3 object name. If not specified, file_name is used.
    :return: The S3 object name if the file was uploaded successfully, else None.
    """

    # Create an S3 client
    s3_client = boto3.client('s3',
        region_name='us-east-1',
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"])

    try:
        # Upload the file
        s3_client.upload_file(file_name, bucket_name, object_name, ExtraArgs={'Metadata': metadata})
        print(f"File {file_name} uploaded to {bucket_name}/{object_name}.")
        return object_name
    except FileNotFoundError:
        print(f"The file {file_name} was not found.")
        return None
    except NoCredentialsError:
        print("Credentials not available.")
        return None
    except PartialCredentialsError:
        print("Incomplete credentials provided.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def list_s3_bucket_items(bucket_name):
    """
    List all items in an S3 bucket.

    :param bucket_name: Name of the S3 bucket.
    :return: A list of object keys in the bucket.
    """
    # Create an S3 client
    s3_client = boto3.client('s3',
        region_name='us-east-1',
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"])

    # List to store all object keys
    object_keys = []

    try:
        # Pagination to handle large number of objects
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket_name)

        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    object_keys.append(obj['Key'])
                    #print(obj['Key'])  # Print each object's key

    except Exception as e:
        print(f"An error occurred: {e}")

    return object_keys

# import re
# def make_safe_filename(s: str) -> str:
#     """Creates a filesystem-safe filename from a string, allowing spaces."""
#     # Allow letters, numbers, underscores, hyphens, dots, and spaces
#     return re.sub(r'[^A-Za-z0-9_\-\. ]+', '', s)

# def update_csv(csv_fpath, bucket_name="text2videoviewer"):
#     all_objects = list_s3_bucket_items(bucket_name)
#     records = []
#     for obj in all_objects:
#         # Split the object name into model and the rest
#         parts = obj.split("/", 1)
#         if len(parts) != 2:
#             continue  # Skip if the object name doesn't match expected pattern
#         model = parts[0]
#         filename = parts[1]

#         # Remove the file extension to get the prompt
#         prompt = filename.rsplit(".", 1)[0]
#         #prompt = make_safe_filename(prompt)

#         # No longer removing commas from prompts
#         records.append({"model": model, "prompt": prompt, "object_name": obj})

#     # Save as CSV with proper quoting
#     df = pd.DataFrame(records)
#     print("Found a total of {} videos in S3.".format(len(records)))

#     # Filter to SOTA models only
#     sota_models = ["cog", "pyramidflow", "opensora"]
#     df = df[df["model"].isin(sota_models)]

#     # Filter prompts in prompts.csv only
#     df = df[df["prompt"].isin(pd.read_csv("prompts.csv")["prompt"])]
#     # Print number of prompts filtered out and number of prompts kept
#     print(f"Filtered out  videos.")
#     print(f"Kept {len(df)} videos.")

#     # Print each kept prompt
#     for model in df["model"].unique():
#         print(f"Kept prompts for model {model} ({len(df[df["model"] == model]["prompt"].unique())} videos):")
#         for prompt in df[df["model"] == model]["prompt"].unique():
#             print(f"\t{prompt}") 
#         print(f"Excluded prompts for model  {model} ({len(records) - len(df)} videos):")
#         excluded_prompts = set(pd.read_csv("prompts.csv")["prompt"]) - set(df[df["model"] == model]["prompt"].unique())
#         for prompt in excluded_prompts:
#             print(f"\t{prompt}")


#     # Update name "opensora-v1-2-720p" to "opensora-v1.2"
#     df["model"] = df["model"].replace({"opensora": "opensora-v1.2"})

#     df.to_csv(csv_fpath, index=False, quoting=csv.QUOTE_ALL, encoding='utf-8')


def get_s3_object_metadata(bucket_name, object_name):
    # Initialize S3 client
    s3_client = boto3.client('s3')
    
    try:
        # Get the object's metadata
        response = s3_client.head_object(Bucket=bucket_name, Key=object_name)
        
        # Return the metadata from the response (stored in the "Metadata" field)
        return response.get("Metadata", {})
    
    except Exception as e:
        print(f"Error retrieving metadata for object {object_name} in bucket {bucket_name}: {str(e)}")
        return {}


def clean_prompt(prompt):
    """
    Cleans up the prompt by stripping leading/trailing newlines or quotation marks.
    
    :param prompt: The prompt string.
    :return: The cleaned prompt string.
    """
    if prompt.startswith(r'\ n'):
        prompt = prompt[3:]
    # remove comma anywhere in prompt
    prompt = prompt.replace(",", "")
    prompt = prompt.replace("'", "")
    return prompt.strip().strip('"').strip("'")

def rename_s3_objects(bucket_name):
    """
    Renames all objects in the specified S3 bucket to ensure the 'prompt' part 
    of the key does not contain trailing or leading newline characters or 
    quotation marks.
    
    :param bucket_name: Name of the S3 bucket.
    """

    # Initialize S3 client
    s3_client = boto3.client('s3',
        region_name='us-east-1',
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"])

    # List all objects in the bucket
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    
    if 'Contents' not in response:
        print(f"No objects found in bucket {bucket_name}.")
        return

    for obj in response['Contents']:
        old_key = obj['Key']
        
        # Assuming object keys follow the format <bucket-name>/<model-name>/prompt
        parts = old_key.split('/')
        if len(parts) < 2:
            print(f"Skipping object with key: {old_key}. Invalid format.")
            continue
        
        # Clean the prompt part of the key
        model_name = parts[0]
        prompt = parts[1]
        cleaned_prompt = clean_prompt(prompt)
        
        if cleaned_prompt != prompt:
            # Create the new object key
            new_key = f"{model_name}/{cleaned_prompt}"
            
            # Copy the object to the new key
            #s3_client.copy_object(Bucket=bucket_name, CopySource={'Bucket': bucket_name, 'Key': old_key}, Key=new_key)
            
            # Check if new key exists
            response = s3_client.list_objects_v2(Bucket=bucket_name)
            if new_key in [obj['Key'] for obj in response['Contents']]:
                s3_client.delete_object(Bucket=bucket_name, Key=old_key)

            else:
                print(f"Need to rename {old_key} to {new_key}.")
                response = input(f"ok? (y/n): ", default='y')
            
            #print(f"Renamed {old_key} to {new_key}.")
        else:
            print(f"No renaming needed for {old_key}.")



def list_model_prompts_in_s3(bucket_name, model_name):
    """
    List all prompts for a specific model in the S3 bucket.

    :param bucket_name: Name of the S3 bucket.
    :param model_name: Name of the model to filter objects by.
    :return: A list of prompts for the model.
    """
    s3_client = boto3.client('s3',
        region_name='us-east-1',
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"])

    # List to store the prompts
    prompts = []

    # List all objects in the bucket
    paginator = s3_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name, Prefix=model_name)

    for page in pages:
        if 'Contents' in page:
            for obj in page['Contents']:
                prompt = obj['Key'].split("/")[1].split(".")[0]
                prompt = prompt.strip().strip('"').strip("'").strip('\n')
                prompts.append(prompt)

    return prompts

def compare_prompts(bucket_name, model_a, model_b):
    """
    Compares the prompts in two models and returns the differences.
    
    :param bucket_name: S3 bucket name.
    :param model_a: Name of the first model.
    :param model_b: Name of the second model.
    :return: Two lists of prompts. One not in Model A and one not in Model B.
    """
    # Get prompts from both models
    prompts_a = set(list_model_prompts_in_s3(bucket_name, model_a))
    prompts_b = set(list_model_prompts_in_s3(bucket_name, model_b))

    # Find prompts that are not in each model
    prompts_not_in_a = list(prompts_b - prompts_a)
    prompts_not_in_b = list(prompts_a - prompts_b)

    print("Prompt in", model_a, "but not in", model_b, ":\n")
    for p in prompts_not_in_b:
        print(p)

    print("\n")
    print("Prompt in", model_b, "but not in", model_a, ":\n")
    print()
    for p in prompts_not_in_a:
        print(p)