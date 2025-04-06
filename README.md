# AltoGPT

AltoGPT is an AI-powered system that integrates with building sensor data to provide intelligent insights and automation capabilities.

## Features

-  **Building Sensor Integration**: Connect with various building sensors to collect real-time data


## Architecture

The system consists of:
- **Backend**: FastAPI server that processes sensor data and provides API endpoints
- **Frontend**: React-based web interface for user interaction
- **MCP Tools**: protocol that standardizes how applications provide context to LLMs.

## Installation

### Prerequisites
* Docker and Docker Compose (for containerized deployment)
* Python
* Node.js
* uv (Python package manager)

### Backend Setup
```bash
# Set up the Python environment
cd backend
uv sync

# Create environment variables file from template
cp .env.example .env
# Edit the .env file with your configuration
```

## Usage

### Tools Component
The Tools Component serves as middleware between the building sensors and the backend system.

```bash
# Start building sensor MCP server
python backend/app/mcp_tools.py
```

This service handles:
- Data collection from physical sensors
- Initial processing and formatting of sensor data
- Communication with the main backend API

### API

#### Configuration
Configure the API by setting environment variables:

```bash
# Option 1: Create .env file in the project root
cp .env.example .env
# Then edit the .env file with your API keys and configuration

# Option 2: Set environment variables directly
export GOOGLE_API_KEY=your_api_key_here
```

#### Starting the API Server
```bash
# Navigate to the backend directory
cd backend

# Start the FastAPI server
fastapi run app/api/main.py
```

The API will be available at http://localhost:8000 with documentation at http://localhost:8000/docs

### Frontend
The frontend provides an intuitive web interface for interacting with AltoGPT.

#### Prerequisites
* Node.js
* npm or yarn

#### Setup and Development
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The development server will be available at http://localhost:5173


### Docker Deployment
For a complete containerized deployment of all components:

```bash
# Build and start all services
docker compose up
```
