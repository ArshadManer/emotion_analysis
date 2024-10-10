# Use an official Python runtime as a base image
FROM python:3.9-slim

# Install system dependencies for dlib and OpenCV
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk2.0-dev \
    libboost-all-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install dlib opencv-python boto3 Pillow

# Set working directory
WORKDIR /app

# Copy the application files
COPY app.py /app/

# Set the entrypoint command to run the application
CMD ["python", "app.py"]
