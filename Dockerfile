FROM python:3.10-slim

# Install ffmpeg and dependencies
RUN apt update && apt install -y ffmpeg curl && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy app files
COPY . .

# Install Python packages
RUN pip install -r requirements.txt

# Create output folder
RUN mkdir -p /app/output

# Expose port
EXPOSE 8080

# Run app
CMD ["python", "app.py"]
