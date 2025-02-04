# Use the official Python image as the base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8080

# Set environment variables for FastAPI
ENV UVICORN_HOST=0.0.0.0
ENV UVICORN_PORT=8080

# Command to run the application
CMD ["uvicorn", "feedback_chain:app", "--host", "0.0.0.0", "--port", "8080"]
