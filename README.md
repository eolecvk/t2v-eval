# t2v-eval

[t2v-eval.com](https://t2v-eval.com) is a solution to compare state-of-the-art open source text-to-video (T2V) models visually.

Models featured:
* [OpenSora v1.2](https://github.com/hpcaitech/Open-Sora)
* [CogVideo](https://github.com/THUDM/CogVideo)
* [PyramidFlow](https://github.com/gasharper/PyramidFlow)

*We are working to include the best open-source T2V models available.*


## Usage

**Setup**

Models weights are downloaded from HuggingFace and videos are stored on AWS.
Running inference and frontend assumes that a HuggingFace account and a AWS S3 bucket are setup.

Prepare env variable file at `/home/ubuntu/text2vid-viewer/.env`
```
AWS_ACCESS_KEY_ID=<your-access-key-id>
AWS_SECRET_ACCESS_KEY=<your-secret-access-key>
AWS_REGION=us-east-1
HF_TOKEN=<your-hf-token>
```

**Inference**
```bash
/bin/bash run_inference.sh --model <model-name>
```

**frontend**
```bash
/bin/bash run_frontend.sh
```

Then, open your browser at http://<instance_IP>:8000/