# Python slim image as base image
FROM python:3.9-slim

# build arguments declared
ARG FLASK_SECRET_KEY
ARG API_SECRET_KEY

# working directory
WORKDIR /app

#  environment variables 
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_SECRET_KEY=$FLASK_SECRET_KEY \
    API_SECRET_KEY=$API_SECRET_KEY

# Install system dependencies 
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc curl && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements file first to leverage Docker cache
COPY requirements.txt ./ 
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a log directory to store application logs
RUN mkdir -p /app/logs

# Expose port
EXPOSE 8000

# Set health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "app.py"]
