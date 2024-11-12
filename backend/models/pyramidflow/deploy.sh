#!/bin/bash

git clone https://github.com/jy0205/Pyramid-Flow
cd Pyramid-Flow

# path inference script
cp /home/ubuntu/text2vid-viewer/backend/models/pyramidflow/inference.py /home/ubuntu/Pyramid-Flow/inference.py

# create env using conda
if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
    . "$HOME/miniconda3/etc/profile.d/conda.sh"
else
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
        bash /tmp/miniconda.sh -b -p $HOME/miniconda3 && \
        rm /tmp/miniconda.sh
    export PATH="$HOME/miniconda3/bin:$PATH"
    conda init
    source ~/.bashrc
    # Add a delay to ensure the environment is set properly
    sleep 2  # Sleep for 2 seconds to allow the environment to refresh
fi

conda init bash
source ~/.bashrc

conda create -n pyramid python=3.8.10 -y
source activate pyramid
pip install -r requirements.txt
pip install pandas


python /home/ubuntu/Pyramid-Flow/inference.py \
    --prompt_path /home/ubuntu/text2vid-viewer/prompts.txt