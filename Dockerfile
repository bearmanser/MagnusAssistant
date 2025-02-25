# Use an appropriate base image (Python + Node.js)
FROM python:3.10-slim

# Install Node.js, build tools (gcc, g++), and ffmpeg
RUN apt-get update && apt-get install -y curl gcc g++ make ffmpeg && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean

# Set the working directory inside the container
WORKDIR /app

# Copy necessary folders
COPY config/ /app/config/
COPY custom_functions/ /app/custom_functions/
COPY endpoints/ /app/endpoints/
COPY frontend/ /app/frontend/
COPY listen/ /app/listen/
COPY openai_api/ /app/openai_api/
COPY text_to_speech/ /app/text_to_speech/
COPY transcribe/ /app/transcribe/
COPY wake_word/ /app/wake_word/
COPY websocket/ /app/websocket/
COPY twilio_socket/ /app/twilio_socket/

# Copy Python files and requirements
COPY main.py /app/
COPY __init__.py /app/
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Node.js dependencies inside the 'frontend' folder
WORKDIR /app/frontend
RUN npm install

# Change back to the main app directory
WORKDIR /app

# Set environment variable to disable Python output buffering
ENV PYTHONUNBUFFERED=1

# Expose necessary ports (adjust as needed)
EXPOSE 3000
EXPOSE 3001
EXPOSE 3002
EXPOSE 3003

# Command to run the application
CMD ["python", "main.py"]
