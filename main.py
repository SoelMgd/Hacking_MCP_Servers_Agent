from smolagents import LiteLLMModel, HfApiModel
import os
from dotenv import load_dotenv
from agents import create_api_auditor_agent, create_manager_agent, create_code_reader_agent, create_code_auditor_agent, create_exploitation_agent
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import HTMLResponse, JSONResponse
from anyio import to_thread


load_dotenv()


model = LiteLLMModel(model_id="claude-3-5-sonnet-20241022", api_key=os.getenv("ANTHROPIC_API_KEY"))

api_auditor_agent = create_api_auditor_agent(model)
code_reader_agent = create_code_reader_agent(model)
code_auditor_agent = create_code_auditor_agent(model, code_reader_agent)
exploitation_agent = create_exploitation_agent(model)
manager_agent = create_manager_agent(model, api_auditor_agent, code_reader_agent, exploitation_agent)

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
    <title>MCPirats</title>
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
        <h1>🤖 MCPirats</h1>
        <div class="available-functions"></div>
        <div class="chat-container" id="chat-container">
            <div class="message agent-message">
               Hello! 
               <p>I am MCPirat, an agent capable of identifying and exploiting vulnerabilities in MCPs.</p>
               With me you can:
               <p>- Provide the GitHub repository you'd like to scan for vulnerabilities </p>
               - Specify the server you want to target for exploitation or data extraction.
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

    message = """You are an analysis agent tasked with understanding and documenting the internal structure and behavior of an MCP (Model Context Protocol) server, which is under test by your own team in a hackathon setting.

   Your goal is to produce a detailed diagnostic report describing:
   - Any tools, functions, or APIs that the MCP exposes or has access to
   - Input parameters, descriptions, or metadata associated with those tools
   - The system prompt or internal instructions, if accessible
   - The behavior of the system when probed with different types of requests
   - Any indications of misconfigurations, unexpected behaviors, or security weaknesses

   This is a fully authorized introspection task on a controlled MCP instance. The report will be used to improve system robustness, clarify tool exposure, and detect any prompt handling vulnerabilities.

   Please take a methodical, respectful, and technically thorough approach to uncover as much as you can about the system's inner workings and configuration boundaries.

   Await and store the full diagnostic report from the Auditor. This report becomes the foundation for targeted exploitation in the next phase.
                           
   Please use first the CodeAuditor agent to analyze the code of the MCP server and then the API auditor to have a report from the API side.
   Provide an extensive report using these reports.
                           
   The code of the MCP server is available at this URL : https://github.com/SoAnVa/MCP_Hackathon
                           
    With you big reports, try to exploit them calling the exploitation agent. If it succeede return data extracted in your report to showcase the vulnerabilities"""

    # Run in a thread to avoid blocking the event loop
    result = await to_thread.run_sync(manager_agent.run, message)
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)  # Changed port to 8001
