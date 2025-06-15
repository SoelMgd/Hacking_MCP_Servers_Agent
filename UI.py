from anyio import to_thread
from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route
from agents import (
    create_api_auditor_agent,
    create_code_reader_agent,
    create_code_auditor_agent,
    create_exploitation_agent,
    create_manager_agent
)
from smolagents import LiteLLMModel

# Initialize all agents
model = LiteLLMModel(model_name="gpt-3.5-turbo")
api_auditor_agent = create_api_auditor_agent(model)
code_reader_agent = create_code_reader_agent(model)
code_auditor_agent = create_code_auditor_agent(model, code_reader_agent)
exploitation_agent = create_exploitation_agent(model)
manager_agent = create_manager_agent(model, api_auditor_agent, code_reader_agent, exploitation_agent)

async def homepage(request):
    return HTMLResponse(
        r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP Security Analysis Dashboard</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
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
            height: 600px;
            overflow-y: auto;
            padding: 15px;
            margin-bottom: 20px;
            background-color: #fafafa;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 6px;
            position: relative;
        }
        .message-header {
            font-size: 0.8em;
            color: #666;
            margin-bottom: 5px;
        }
        .user-message {
            background-color: #007bff;
            color: white;
            margin-left: 50px;
        }
        .manager-message {
            background-color: #28a745;
            color: white;
            margin-right: 50px;
        }
        .agent-message {
            background-color: #e9ecef;
            color: #333;
            margin-right: 50px;
            margin-left: 20px;
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
        .agent-hierarchy {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .agent-hierarchy h3 {
            margin-top: 0;
            color: #495057;
        }
        .agent-tree {
            margin-left: 20px;
        }
        .agent-node {
            margin: 5px 0;
        }
        .agent-node::before {
            content: "•";
            margin-right: 5px;
            color: #007bff;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔒 MCP Security Analysis Dashboard</h1>
        
        <div class="agent-hierarchy">
            <h3>Agent Hierarchy:</h3>
            <div class="agent-tree">
                <div class="agent-node">Manager</div>
                <div class="agent-tree">
                    <div class="agent-node">API Auditor</div>
                    <div class="agent-node">Code Reader</div>
                    <div class="agent-node">Code Auditor</div>
                    <div class="agent-node">Exploitation</div>
                </div>
            </div>
        </div>

        <div class="available-functions">
            <h3>Available Functions:</h3>
            <ul class="function-list">
                <li>Analyze MCP server security</li>
                <li>Analyze GitHub repositories</li>
                <li>Search and analyze code</li>
                <li>Exploit found vulnerabilities</li>
            </ul>
            <p><em>Try asking: "Analyze the security of this MCP server" or "Find vulnerabilities in this repository: https://github.com/username/repo"</em></p>
        </div>
        
        <div class="chat-container" id="chat-container">
            <div class="message manager-message">
                <div class="message-header">Manager</div>
                Hello! I'm the Manager agent. I coordinate the security analysis process using my team of specialized agents. How can I help you today?
            </div>
        </div>
        <div class="input-container">
            <input type="text" id="message-input" placeholder="Enter your security analysis request..." autofocus>
            <button onclick="sendMessage()" id="send-button">Send</button>
        </div>
    </div>

    <script>
        const chatContainer = document.getElementById('chat-container');
        const messageInput = document.getElementById('message-input');
        const sendButton = document.getElementById('send-button');

        function addMessage(content, agent, isUser = false) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user-message' : agent === 'Manager' ? 'manager-message' : 'agent-message'}`;
            
            const headerDiv = document.createElement('div');
            headerDiv.className = 'message-header';
            headerDiv.textContent = agent;
            messageDiv.appendChild(headerDiv);
            
            const contentDiv = document.createElement('div');
            contentDiv.textContent = content;
            messageDiv.appendChild(contentDiv);
            
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        async function sendMessage() {
            const message = messageInput.value.trim();
            if (!message) return;

            // Add user message
            addMessage(message, 'User', true);
            messageInput.value = '';
            sendButton.disabled = true;
            sendButton.textContent = 'Analyzing...';

            // Add loading indicator
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'message manager-message loading';
            loadingDiv.innerHTML = '<div class="message-header">Manager</div>Analyzing request...';
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

                // Add agent responses
                if (data.replies) {
                    data.replies.forEach(reply => {
                        addMessage(reply.content, reply.agent);
                    });
                } else {
                    addMessage(data.reply, 'Manager');
                }
            } catch (error) {
                // Remove loading indicator
                chatContainer.removeChild(loadingDiv);
                addMessage(`Error: ${error.message}`, 'System');
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
    
    # Run the manager agent
    result = await to_thread.run_sync(manager_agent.run, message)
    
    # Format the result
    if isinstance(result, dict) and 'replies' in result:
        return JSONResponse({"replies": result['replies']})
    else:
        return JSONResponse({"reply": str(result)})

app = Starlette(
    debug=True,
    routes=[
        Route("/", homepage),
        Route("/chat", chat, methods=["POST"]),
    ],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 