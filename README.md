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
# Add OpenSora inference script [2024-08-29T10:47:00]

# Refactor CogVideo inference pipeline [2024-08-31T12:55:00]

# Adjust PyramidFlow latent noise scale [2024-09-04T11:41:00]

# Unify inference entrypoint for all models [2024-09-07T15:50:00]

# Clean up old S3 buckets for stale models [2024-09-09T17:41:00]

# Implement lazy loading for videos on scroll [2024-09-10T12:56:00]

# Add toggle for showing only recent generations [2024-09-14T17:30:00]

# Create .env template with example values [2024-09-17T16:57:00]

# Test long descriptive prompts across all models [2024-09-20T18:30:00]

# Add video resolution check to CI step [2024-09-23T09:57:00]

# Add OpenSora inference script [2024-09-23T12:47:00]

# Refactor CogVideo inference pipeline [2024-09-25T15:34:00]

# Adjust PyramidFlow latent noise scale [2024-09-29T10:26:00]

# Unify inference entrypoint for all models [2024-10-03T12:38:00]

# Clean up old S3 buckets for stale models [2024-10-06T17:51:00]

# Implement lazy loading for videos on scroll [2024-10-09T18:20:00]

# Add toggle for showing only recent generations [2024-10-12T18:42:00]

# Create .env template with example values [2024-10-17T17:24:00]

# Test long descriptive prompts across all models [2024-10-19T10:53:00]
