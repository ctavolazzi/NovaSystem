#!/bin/bash
# NovaSystem Environment Setup Script

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up NovaSystem environment...${NC}"

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
major=$(echo "${python_version}" | cut -d. -f1)
minor=$(echo "${python_version}" | cut -d. -f2)

echo -e "${YELLOW}Detected Python version: ${python_version}${NC}"

if [[ "${major}" -lt 3 || ("${major}" -eq 3 && "${minor}" -lt 10) ]]; then
    echo -e "${RED}Error: Python 3.10+ is required. Please install a newer version.${NC}"
    exit 1
fi

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}Ollama not found. Installing instructions:${NC}"
    echo -e "1. Visit https://ollama.com/download"
    echo -e "2. Follow the installation instructions for your platform"
    echo -e "3. After installation, run: ollama pull llama3"
    echo -e "4. Run: ollama serve (in a separate terminal)"
    echo -e "${YELLOW}Please install Ollama and re-run this script.${NC}"

    # Ask if user wants to continue without Ollama
    read -p "Continue setup without Ollama? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}Ollama found. Checking for required models...${NC}"

    # Check if llama3 model is available, pull if not
    if ! ollama list | grep -q "llama3"; then
        echo -e "${YELLOW}Downloading llama3 model (this might take a while)...${NC}"
        ollama pull llama3
    else
        echo -e "${GREEN}llama3 model already available${NC}"
    fi

    # Check if Ollama is running
    if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        echo -e "${YELLOW}Ollama is not running. Starting Ollama...${NC}"

        # Start Ollama in the background
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            open -a Ollama
            echo -e "${YELLOW}Waiting for Ollama to start...${NC}"
            sleep 5
        else
            # Linux
            echo -e "${YELLOW}Please start Ollama manually with 'ollama serve' in a separate terminal.${NC}"
        fi
    else
        echo -e "${GREEN}Ollama is running${NC}"
    fi
fi

# Create virtual environments for backend
echo -e "${GREEN}Creating virtual environment for backend...${NC}"
cd backend || exit 1
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
echo -e "${GREEN}Installing backend dependencies...${NC}"
pip install --upgrade pip
pip install fastapi uvicorn sqlalchemy pydantic python-dotenv httpx pytest pytest-asyncio
pip freeze > requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file with default configuration...${NC}"
    cat > .env << EOF
# NovaSystem Environment Configuration

# Database
DATABASE_URL=sqlite:///./novasystem.db

# LLM Providers
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
DEFAULT_OLLAMA_MODEL=llama3
USE_LOCAL_LLM=true

# Server
PORT=8000
HOST=0.0.0.0
DEBUG=True
EOF
    echo -e "${YELLOW}Created .env file with Ollama configured as the default provider.${NC}"
    echo -e "${YELLOW}If you want to use OpenAI instead, set USE_LOCAL_LLM=false in the .env file.${NC}"
fi

# Deactivate virtual environment
deactivate

cd ..

# Create directory for database
echo -e "${GREEN}Creating database directory...${NC}"
mkdir -p backend/data

# Create empty README.md files for empty directories
echo -e "${GREEN}Creating placeholder README.md files...${NC}"
mkdir -p frontend/src/{components,routes,lib,stores}

for dir in frontend/src/components frontend/src/routes frontend/src/lib frontend/src/stores; do
    if [ ! -f "$dir/README.md" ]; then
        echo "# ${dir##*/}" > "$dir/README.md"
        echo "This directory contains ${dir##*/} for the NovaSystem frontend." >> "$dir/README.md"
    fi
done

# Create basic git ignore file
if [ ! -f .gitignore ]; then
    echo -e "${GREEN}Creating .gitignore file...${NC}"
    cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/
.env
.venv
*.egg-info/
.installed.cfg
*.egg

# Database
*.db
*.sqlite3

# Logs
*.log
logs/

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/

# Node.js
node_modules/
npm-debug.log
yarn-debug.log
yarn-error.log
.pnpm-debug.log
.npm
.yarn

# Build output
/dist
/build
/.svelte-kit
/.next
/out

# IDE
.idea/
.vscode/
*.swp
*.swo
*~
.DS_Store
EOF
fi

echo -e "${GREEN}Environment setup complete!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Make sure Ollama is running with: ${YELLOW}ollama serve${NC}"
echo -e "2. Start the backend server: ${YELLOW}cd backend && source venv/bin/activate && python -m api.main${NC}"
echo -e "3. Set up the frontend: ${YELLOW}cd frontend && npm install && npm run dev${NC}"

echo -e "${GREEN}NovaSystem is now configured to use Ollama as the default LLM provider!${NC}"
echo -e "${YELLOW}Available models in Ollama:${NC}"
ollama list

echo -e "${GREEN}Happy developing!${NC}"