# Use Python slim image as base image
FROM python:3.9-slim

# Declare build arguments
ARG FLASK_SECRET_KEY
ARG API_SECRET_KEY

# Set working directory
WORKDIR /app

# Set environment variables using the build args
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_SECRET_KEY=$FLASK_SECRET_KEY \
    API_SECRET_KEY=$API_SECRET_KEY

# Install system dependencies (e.g., curl if needed)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc curl && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements file first to leverage Docker cache
COPY requirements.txt ./ 
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create a log directory to store application logs
RUN mkdir -p /app/logs

# Expose the port the app will run on
EXPOSE 8000

# Set health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "app.py"]
