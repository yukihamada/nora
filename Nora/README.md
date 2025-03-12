# Nora - Autonomous Software Development Agent

Nora is an autonomous software development agent inspired by DEVIN and built on OpenHands. It can browse the web, generate code, test, manage GitHub repositories, deploy to cloud platforms, manage domains, monetize applications, and run ad campaigns.

## Features

- **Web Browsing**: Collect the latest technical information and code examples from the web
- **Code Generation**: Generate code in any language (Python, JavaScript, etc.) based on collected information
- **Testing**: Test generated code and fix errors
- **GitHub Management**: Commit and push code to GitHub repositories
- **Cloud Deployment**: Deploy code to cloud platforms (AWS, Google Cloud, etc.)
- **Domain Management**: Purchase domains and configure DNS
- **Monetization**: Set up subscriptions with Stripe and ads with Google AdSense
- **Ad Campaigns**: Set up and manage Google Ads campaigns

## Installation

### Option 1: Standard Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/nora-agent.git
cd nora-agent

# Run the setup script
./setup.sh
```

The setup script will:
1. Create necessary directories
2. Create a `.env` file from the example if it doesn't exist
3. Install Python dependencies
4. Install Node.js dependencies

### Option 2: Docker Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/nora-agent.git
cd nora-agent

# Create .env file
cp config/.env.example config/.env

# Edit the .env file to add your API keys
nano config/.env

# Build and run with Docker Compose
docker-compose up -d
```

## Configuration

1. Create a `.env` file in the `config` directory based on the `config/.env.example` template
2. Add your API keys and credentials to the `.env` file

## Usage

### Standard Usage

```bash
python main.py
```

### Docker Usage

```bash
docker-compose up -d
```

## Project Structure

```
Nora/
├── main.py                    # Agent execution entry point (Python-based)
├── package.json               # JavaScript dependencies
├── requirements.txt           # Python dependencies
├── README.md                  # Project overview and usage
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose configuration
├── setup.sh                   # Setup script
├── src/                       # Source code
│   ├── agents/                # Custom OpenHands agents
│   ├── tools/                 # Custom tools
│   └── core/                  # OpenHands core functionality
├── utils/                     # Utilities
├── config/                    # Configuration
├── data/                      # Data management
└── tests/                     # Tests
```

## Development

### Running Tests

```bash
python -m unittest discover tests
```

### Adding New Agents

To add a new agent:

1. Create a new file in the `src/agents` directory
2. Implement the agent class with an `execute` method
3. Register the agent in `src/core/agent_runner.py`

### Adding New Tools

To add a new tool:

1. Create a new file in the `src/tools` directory
2. Implement the tool class with appropriate methods
3. Import and use the tool in the relevant agent

## License

MIT

## Acknowledgements

- [OpenHands](https://github.com/All-Hands-AI/OpenHands) - Base framework
- DEVIN - Inspiration for autonomous development capabilities