#!/bin/bash

# Nora setup script

# Create necessary directories
mkdir -p data/cache data/logs data/generated data/deployments

# Create .env file from example if it doesn't exist
if [ ! -f config/.env ]; then
    echo "Creating .env file from example..."
    cp config/.env.example config/.env
    echo "Please edit config/.env to add your API keys and credentials."
fi

# Check if Python is installed
if command -v python3 &>/dev/null; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
else
    echo "Python 3 is not installed. Please install Python 3 and pip."
    exit 1
fi

# Check if Node.js is installed
if command -v node &>/dev/null; then
    echo "Installing Node.js dependencies..."
    npm install
else
    echo "Node.js is not installed. Some features may not work properly."
fi

echo "Setup complete! You can now run Nora with: python main.py"