# Use an official Python 3.11 slim image as the base
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# We need the "netcat" tool for our entrypoint script to work.
RUN apt-get update && apt-get install -y --no-install-recommends netcat-openbsd &&     rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY ./requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your backend application code into the container
COPY . .

# Make our entrypoint script executable
RUN chmod +x ./entrypoint.sh
