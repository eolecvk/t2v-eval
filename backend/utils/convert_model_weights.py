import torch
from safetensors.torch import save_file
import json
import os

def convert(input_dpath, output_dpath):
    """
    Converts model weights from .pt or bin format to .safetensors.
    Supports two workflows:
    1. When there's a JSON file that maps the weights to binary files.
    2. When model weights are stored in .pt files directly.
    """

    # Check if the input directory contains a JSON file for the weight map (workflow 1)
    json_file = f'{input_dpath}/pytorch_model.bin.index.json'
    if os.path.exists(json_file):
        # Workflow 1: Using JSON file to map tensors to binary files
        with open(json_file, 'r') as f:
            data = json.load(f)

        weight_map = data['weight_map']

        # Initialize a dictionary to hold the model's tensors
        model_weights = {}

        # Load the weights from the binary files
        for param_name, bin_file in weight_map.items():
            bin_file = f"{input_dpath}/{bin_file}"
            # Ensure the bin file exists
            if not os.path.exists(bin_file):
                raise FileNotFoundError(f"File {bin_file} not found")
            # Load the specific tensor from the bin file
            tensor = torch.load(bin_file, map_location='cpu')[param_name]
            model_weights[param_name] = tensor

        # Save all the tensors into a single safetensor file
        save_file(model_weights, f'{output_dpath}/model.safetensors', metadata={'format': 'pt'})
        print("Model successfully converted to safetensors (workflow 1)!")
    
    else:
        # Workflow 2: Load .pt files from the input directory directly (e.g., Models folder)
        pt_files = [f for f in os.listdir(input_dpath) if f.endswith('.pt')]
        
        if not pt_files:
            raise FileNotFoundError("No .pt files found in the input directory.")

        for pt_file in pt_files:
            # Load each .pt file and convert it to safetensors
            file_path = os.path.join(input_dpath, pt_file)
            state_dict = torch.load(file_path, map_location='cpu')

            # Define the output .safetensors file name
            safetensors_file = pt_file.replace(".pt", ".safetensors")
            safetensors_path = os.path.join(output_dpath, safetensors_file)

            # Save the state_dict as a safetensors file with metadata
            save_file(state_dict, safetensors_path, metadata={'format': 'pt'})
            print(f"Converted {pt_file} to {safetensors_file} with metadata format='pt'")
        
        print("All .pt files successfully converted to safetensors (workflow 2)!")


if __name__ == '__main__':
    input_dpath = "/home/ubuntu/models--lambdalabs--OpenSora-STDiT-v3-Lambda/snapshots/5cde91be1df6da56b6b70ed5e943e0bc2cb38b9b/model"
    output_dpath = "/home/ubuntu"
    convert(input_dpath, output_dpath)
