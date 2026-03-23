FROM nvidia/cuda:12.8.0-cudnn-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    software-properties-common \
    curl \
    gcc \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3.11-distutils \
    && rm -rf /var/lib/apt/lists/*

# set python3.11 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1 \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# install pip using get-pip.py
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# verify
RUN python --version && pip --version

WORKDIR /app

RUN pip install --upgrade pip

COPY docker_requirements.txt .

# Step 1 — torch from PyTorch index
RUN pip install \
    torch==2.10.0+cu128 \
    torchvision==0.25.0+cu128 \
    --index-url https://download.pytorch.org/whl/cu128

# Step 2 — everything else
RUN pip install -r docker_requirements.txt --ignore-installed

COPY . .

RUN mkdir -p static/uploaded_leaves

EXPOSE 5000

CMD ["python", "main.py"]