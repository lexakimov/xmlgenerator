FROM python:3.13-slim

#RUN apt-get update && apt-get install -y clang-19 patchelf && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y build-essential patchelf && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --progress-bar off --no-cache-dir -r requirements.txt

ENTRYPOINT [ "python", "build_native.py" ]