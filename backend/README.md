# Quickstart: Running inference

Whether you want to run inference on your own model or run your own prompt, you can use the following guide for inference. 


Clone the repository
```bash
git clone https://github.com/LambdaLabsML/text2vid-viewer.git
```

Prepare env variable file at `/home/ubuntu/text2vid-viewer/.env`
```
AWS_ACCESS_KEY_ID=<your-access-key-id>
AWS_SECRET_ACCESS_KEY=<your-secret-access-key>
AWS_REGION=us-east-1
HF_TOKEN=<your-hf-token>
```

Optionally, write your own prompts in the input prompt file at `/home/ubuntu/text2vid-viewer/prompts.txt`. If not, the default prompts will be used for generation. Note that `prompts.txt` should include one prompt per line.


Optionally, add support for your own models (instructions in progress)


Run inference
```bash
/bin/bash run_inference.sh --model <opensora-v1-2-720p>
```


Note:
* model should have a matching config file in `backend/models/opensora/configs/`
* inference logs are piped to /home/ubuntu/logs/inference.log
* outputs are directly exported to S3
* For opensora model, model config can be edited at `/home/ubuntu/text2vid-viewer/backend/models/opensora/configs/<base-model>-<resolution>.py`

