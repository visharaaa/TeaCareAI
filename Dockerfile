# CUDA 12.8 + cuDNN runtime — matches torch==2.10.0+cu128
FROM nvidia/cuda:12.8.0-cudnn-runtime-ubuntu22.04

# prevent interactive prompts during apt installs
ENV DEBIAN_FRONTEND=noninteractive

# system dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3-pip \
    gcc \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# make python3.11 the default python
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1 \
    && update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

WORKDIR /app

# install uv
RUN pip install uv

# copy requirements first for better layer caching
COPY requirements.txt .

# install all packages
RUN uv pip install -r requirements.txt \
    --system \
    --index-strategy unsafe-best-match

# copy the full project
COPY . .

# create upload folder if not exists
RUN mkdir -p static/uploaded_leaves

EXPOSE 5000

CMD ["python", "main.py"]