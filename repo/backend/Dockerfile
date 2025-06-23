FROM python:3.9-slim

# Set the working directory
WORKDIR /app


RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/app"

# Copy all your project files into the container
COPY . .

