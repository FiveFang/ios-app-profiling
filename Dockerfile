# iOS Battery Testing Web Interface
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt web_requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt -r web_requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads output/device_profiles output/extracted output/results

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Start the web interface
CMD ["python", "web_ui/app.py"]
