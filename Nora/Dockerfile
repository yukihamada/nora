FROM python:3.10-slim

WORKDIR /app

# Install Node.js
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    && curl -sL https://deb.nodesource.com/setup_16.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Node.js dependencies
COPY package.json .
RUN npm install

# Copy the application
COPY . .

# Create necessary directories
RUN mkdir -p data/cache data/logs data/generated data/deployments

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "main.py"]