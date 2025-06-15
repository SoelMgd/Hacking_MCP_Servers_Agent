# MCPirats - MCP Vulnerability Analysis Tool

MCPirats is a sophisticated security analysis tool designed to identify and exploit vulnerabilities in Model Context Protocol (MCP) servers. It uses a multi-agent architecture to perform comprehensive security audits through both code analysis and API probing.

## Architecture

The system consists of several specialized agents working together:

1. **Manager Agent**: Orchestrates the entire analysis process and coordinates between other agents
2. **API Auditor Agent**: Analyzes the MCP server's API endpoints and behavior
3. **Code Reader Agent**: Reads and analyzes code from GitHub repositories
4. **Code Auditor Agent**: Performs security analysis on the codebase
5. **Exploitation Agent**: Attempts to exploit identified vulnerabilities

### Agent Pipeline

1. The Manager Agent receives a task and creates an analysis plan
2. The Code Auditor Agent analyzes the target repository's code
3. The API Auditor Agent probes the MCP server's endpoints
4. The Exploitation Agent attempts to exploit identified vulnerabilities
5. The Manager Agent compiles a comprehensive report

## Setup

### Prerequisites

- Python 3.10 or higher
- An Anthropic API key (for Claude model access)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mcp-hacker
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
```

4. Create a `.env` file in the project root with your API key:
```
ANTHROPIC_API_KEY=your_api_key_here
```

## Running the Application

1. Start the MCP server (target) first:
```bash
cd MCP_Hackathon
uvicorn main:app --host 0.0.0.0 --port 8000
```

2. In a new terminal, start the MCPirats server:
```bash
cd mcp_hacker
uvicorn main:app --host 0.0.0.0 --port 8001
```

3. Open your browser and navigate to `http://localhost:8001`

## Usage

1. Access the web interface at `http://localhost:8001`
2. Enter your analysis request in the chat interface
3. The system will:
   - Analyze the target MCP server's code
   - Probe the API endpoints
   - Attempt to exploit vulnerabilities
   - Provide a comprehensive security report

## Features

- Web-based chat interface for easy interaction
- Multi-agent architecture for comprehensive analysis
- Code and API vulnerability detection
- Automated exploitation attempts
- Detailed security reports

## Security Note

This tool is designed for authorized security testing and educational purposes only. Always ensure you have proper authorization before testing any MCP server.

## Dependencies

- smolagents[litellm]>=1.18.0
- fastapi>=0.115.12
- starlette>=0.36.3
- requests>=2.32.4
- anyio>=4.3.0
- markdownify>=1.1.0
- uvicorn>=0.34.3 
