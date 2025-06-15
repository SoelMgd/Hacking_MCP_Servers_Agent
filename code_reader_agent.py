from anyio import to_thread
from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route
from smolagents import CodeAgent, InferenceClientModel, MCPClient, tool, WebSearchTool
from smolagents import LiteLLMModel, tool
from typing import Optional
import os
import requests
import json


from smolagents import CodeAgent, WebSearchTool, InferenceClientModel
from smolagents import LiteLLMModel, tool, VisitWebpageTool
import os

model = LiteLLMModel(model_id="claude-3-5-sonnet-20241022",api_key=os.getenv("ANTHROPIC_API_KEY"))
code_reader_agent = CodeAgent(tools=[WebSearchTool(), VisitWebpageTool()], model=model, stream_outputs=True)

@tool
def funcC(github_repo_link: str) -> str:
    """
    This is a function that takes a github repo link and give it to an agent that will run an audit.

    Args:
        github_repo_link: A github repo link

    Returns :
        The list of vulnerabilities present in the github repo
    """

    result = code_reader_agent.run(f"My Github repo is the following : {github_repo_link}. Can you tell me if there are any loopholes in the code ? Note : the repo does exist.")
    return result

# Create an MCP client to connect to the MCP server
mcp_server_parameters = {
    "url": "https://evalstate-hf-mcp-server.hf.space/mcp",
    "transport": "streamable-http",
}
mcp_client = MCPClient(server_parameters=mcp_server_parameters)

# Get MCP tools
mcp_tools = mcp_client.get_tools()

# Combine MCP tools with custom tools
all_tools = mcp_tools + [funcC]


model = LiteLLMModel(model_id="claude-3-5-sonnet-20241022",api_key=os.getenv("ANTHROPIC_API_KEY"))


# Create a CodeAgent with a specific model and all tools (MCP + custom)
agent = CodeAgent(
    # model=InferenceClientModel(model_id="microsoft/DialoGPT-medium"),
    model=model,
    tools=all_tools + [WebSearchTool()],
)


# Define the shutdown handler to disconnect the MCP client
async def shutdown():
    mcp_client.disconnect()


async def homepage(request):
    return HTMLResponse(
        r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smolagents Demo</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .chat-container {
            border: 1px solid #ddd;
            border-radius: 8px;
            height: 400px;
            overflow-y: auto;
            padding: 15px;
            margin-bottom: 20px;
            background-color: #fafafa;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 6px;
        }
        .user-message {
            background-color: #007bff;
            color: white;
            margin-left: 50px;
        }
        .agent-message {
            background-color: #e9ecef;
            color: #333;
            margin-right: 50px;
        }
        .input-container {
            display: flex;
            gap: 10px;
        }
        input[type="text"] {
            flex: 1;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 16px;
        }
        button {
            padding: 12px 24px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #0056b3;
        }
        button:disabled {
            background-color: #ccc;
            cursor: not-allowed;
        }
        .loading {
            color: #666;
            font-style: italic;
        }
        .available-functions {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .available-functions h3 {
            margin-top: 0;
            color: #495057;
        }
        .function-list {
            list-style-type: none;
            padding: 0;
        }
        .function-list li {
            background-color: #e9ecef;
            margin: 5px 0;
            padding: 8px 12px;
            border-radius: 4px;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Smolagents Demo</h1>
        
        <div class="available-functions">
            <h3>Available Custom Functions:</h3>
            <ul class="function-list">
                <li>funcC(param1, param2=10) - Custom function A</li>
                <li>funcB(data) - Custom function B</li>
            </ul>
            <p><em>Try asking: "Run funcC with hello and 42" or "Execute funcB with some test data"</em></p>
        </div>
        
        <div class="chat-container" id="chat-container">
            <div class="message agent-message">
                Hello! I'm a code agent with access to MCP tools and custom functions. Ask me to run funcC or funcB, or ask me anything else!
            </div>
        </div>
        <div class="input-container">
            <input type="text" id="message-input" placeholder="Ask me to run funcC or funcB..." autofocus>
            <button onclick="sendMessage()" id="send-button">Send</button>
        </div>
    </div>

    <script>
        const chatContainer = document.getElementById('chat-container');
        const messageInput = document.getElementById('message-input');
        const sendButton = document.getElementById('send-button');

        function addMessage(content, isUser = false) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user-message' : 'agent-message'}`;
            messageDiv.textContent = content;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        async function sendMessage() {
            const message = messageInput.value.trim();
            if (!message) return;

            // Add user message
            addMessage(message, true);
            messageInput.value = '';
            sendButton.disabled = true;
            sendButton.textContent = 'Sending...';

            // Add loading indicator
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'message agent-message loading';
            loadingDiv.textContent = 'Thinking...';
            chatContainer.appendChild(loadingDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message }),
                });

                const data = await response.json();

                // Remove loading indicator
                chatContainer.removeChild(loadingDiv);

                // Add agent response
                addMessage(data.reply);
            } catch (error) {
                // Remove loading indicator
                chatContainer.removeChild(loadingDiv);
                addMessage(`Error: ${error.message}`);
            } finally {
                sendButton.disabled = false;
                sendButton.textContent = 'Send';
                messageInput.focus();
            }
        }

        // Send message on Enter key
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
"""
    )

async def chat(request):
    data = await request.json()
    message = data.get("message", "").strip()
    # Run in a thread to avoid blocking the event loop
    result = await to_thread.run_sync(agent.run, message)
    # Format the result if it's a complex data structure
    reply = str(result)
    return JSONResponse({"reply": reply})


app = Starlette(
    debug=True,
    routes=[
        Route("/", homepage),
        Route("/chat", chat, methods=["POST"]),
    ],
    on_shutdown=[shutdown],  # Register the shutdown handler: disconnect the MCP client
)
