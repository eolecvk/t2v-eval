FROM shivamsphn/opensora:latest

# Install necessary libraries
RUN pip install boto3

# Create the logs directory
RUN mkdir -p /app/logs && chmod -R 777 /app/logs
ENV PYTHONUNBUFFERED=1

# Copy the inference script
COPY backend/models/opensora/inference.py /app/inference.py

# Copy the entire config directory
COPY backend/models/opensora/configs/ /app/custom_configs/

# Copy the prompt file
COPY prompts.txt /app/prompts.txt

# Run the inference script with model and prompt-path arguments
ENTRYPOINT ["python", "/app/inference.py"]
