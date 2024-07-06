# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install any needed packages specified in requirements.txt
RUN apt-get update \
    && apt-get install -y ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Expose port 8000 to allow communication to/from the container
EXPOSE 8000

# Command to run the FastAPI server within the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
