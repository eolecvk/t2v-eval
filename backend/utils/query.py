

import pandas as pd
import requests
import json

csv_fpath = "/home/eole/Workspaces/text2vid-viewer/frontend/db.csv"
df = pd.read_csv(csv_fpath)

prompts = df["prompt"].unique().tolist()

prompts = ["close up shot of a yellow taxi turning left"]

# Define the API endpoint
api_url = "http://209.20.156.111:5000/generate"

# Define the model to use
model = "lambda"  # or 'opensora-v1-1', 'opensora-v1-2'

# Prepare the headers
headers = {
    "Content-Type": "application/json"
}

# Prepare the payload
payload = {
    "model": model,
    "prompt": prompts
}

# Convert payload to JSON string
payload_json = json.dumps(payload)

print(payload_json)
print()

# # Make the POST request
response = requests.post(api_url, headers=headers, data=payload_json)

# Check the response
if response.status_code == 200:
    print("Request was successful.")
    response_data = response.json()
    print(json.dumps(response_data, indent=4))
else:
    print(f"Request failed with status code {response.status_code}")
    print(response.text)
