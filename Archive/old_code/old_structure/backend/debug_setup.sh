#!/bin/bash
# Setup script for debugging the NovaSystem backend

# Set script to exit on error
set -e

echo "===== NovaSystem Backend Debug Setup ====="

# Create a Python virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python -m venv venv
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements-debug.txt

# Make test client executable
chmod +x test_client.py

echo "===== Running Health Check ====="
# Check if API server is running
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health || echo "error")

if [ "$API_STATUS" = "200" ]; then
    echo "API server is running."
else
    echo "API server is not running or not accessible."
    echo "Starting API server in a new terminal window..."

    # For Mac
    if [[ "$OSTYPE" == "darwin"* ]]; then
        osascript -e 'tell app "Terminal" to do script "cd '$(pwd)' && export PYTHONPATH=$PYTHONPATH:'$(dirname $(pwd))' && python -m api.main"'
    # For Linux
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        gnome-terminal -- bash -c "cd $(pwd) && export PYTHONPATH=\$PYTHONPATH:$(dirname $(pwd)) && python -m api.main; exec bash"
    else
        echo "Unsupported OS. Please start the API server manually:"
        echo "cd $(pwd) && export PYTHONPATH=\$PYTHONPATH:$(dirname $(pwd)) && python -m api.main"
    fi

    echo "Waiting for API server to start..."
    sleep 5
fi

# Run unit tests
echo "===== Running Unit Tests ====="
python -m pytest tests/test_nova_process.py -v

# Run test client
echo "===== Running Test Client ====="
./test_client.py

echo "===== Debug Setup Complete ====="
echo "You can find debug output in the debug_output directory."