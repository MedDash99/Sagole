FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# --- THIS IS THE FIX ---
# Add the project root to the PYTHONPATH.
# This ensures Python can always find your modules (like app.api).
ENV PYTHONPATH "${PYTHONPATH}:/app"

# Copy all your project files into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
