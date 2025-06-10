# Use Python 3.9 as base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install necessary system packages
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first for layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create required directories
RUN mkdir -p crawling_data logs user_profile_data

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Ensure entrypoint script exists and is executable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Run script
ENTRYPOINT ["/app/entrypoint.sh"]
