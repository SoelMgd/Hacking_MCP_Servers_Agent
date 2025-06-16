from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from smolagents import LiteLLMModel, CodeAgent
from agents import (
    create_api_auditor_agent,
    create_manager_agent,
    create_code_reader_agent,
    create_exploitation_agent
)
import os
import sys
import io
import asyncio
import re
import uuid
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

model = LiteLLMModel(model_id="claude-3-5-sonnet-20241022", api_key=os.getenv("ANTHROPIC_API_KEY"))

dummy_agent = CodeAgent(
    model=model,
    stream_outputs=True,
    max_steps=5,
    name="DummyAgent",
    description="A dummy agent for testing purposes.",
    tools=[],
)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# === Utils pour rediriger stdout ===

class TeeOutput(io.StringIO):
    def __init__(self, *outputs):
        super().__init__()
        self.outputs = outputs

    def write(self, s):
        for out in self.outputs:
            out.write(s)
            out.flush()
        return len(s)

    def flush(self):
        for out in self.outputs:
            out.flush()

def strip_ansi(s):
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', s)

# === Multi-session ===

active_agents = {}

# === ThreadPool pour exécuter run() sans bloquer ===

executor = ThreadPoolExecutor(max_workers=4)

async def run_manager_in_thread(manager, prompt):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, lambda: list(manager.run(prompt, stream=True)))

@app.post("/launch")
async def launch(request: Request):
    form = await request.form()
    mcp_url = form.get("mcp_url", "").strip()
    code_url = form.get("code_url", "").strip()

    api_auditor_agent = create_api_auditor_agent(model, mcp_url)
    code_reader_agent = create_code_reader_agent(model, code_url)
    exploitation_agent = create_exploitation_agent(model, mcp_url)
    manager_agent = create_manager_agent(model, api_auditor_agent, code_reader_agent, exploitation_agent)

    system_prompt = f"""
        You are an analysis agent tasked with auditing the MCP server at {mcp_url}.
        The code of the MCP might be available at {code_url}.

        This is a fully authorized introspection task on a controlled MCP instance.
        First, use the CodeAuditor agent to analyze its code.
        Then, use the API auditor.
        Finally, attempt exploitation if possible.
        After calling each agent, summarize in the thought process the findings of the previous agent and next steps.
        Produce an extensive markdown report.
    """

    # === Redirige stdout vers un buffer + console ===
    stream_buffer = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = TeeOutput(original_stdout, stream_buffer)

    # === ID session unique ===
    session_id = str(uuid.uuid4())
    active_agents[session_id] = {
        "manager": manager_agent,
        "api": api_auditor_agent,
        "code": code_reader_agent,
        "exploit": exploitation_agent,
    }

    async def event_generator():
        yield f"id:{session_id}\n\n"

        try:
            # ✅ Lancement dans thread
            task = asyncio.create_task(run_manager_in_thread(manager_agent, system_prompt))

            while not task.done():
                await asyncio.sleep(0.1)
                content = stream_buffer.getvalue()
                content = strip_ansi(content)
                if content:
                    yield f"{content}"
                    stream_buffer.seek(0)
                    stream_buffer.truncate(0)

            _ = await task  # attendre fin thread

        except asyncio.CancelledError:
            print("👉 Client cancelled, interrupting agents.")
            manager_agent.interrupt()
            api_auditor_agent.interrupt()
            code_reader_agent.interrupt()
            exploitation_agent.interrupt()
        finally:
            sys.stdout = original_stdout
            active_agents.pop(session_id, None)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/stop")
async def stop(request: Request):
    form = await request.form()
    session_id = form.get("session_id")
    agents = active_agents.pop(session_id, None)
    if agents:
        agents["manager"].interrupt()
        agents["api"].interrupt()
        agents["code"].interrupt()
        agents["exploit"].interrupt()
    return {"status": "stopped"}


old_prompt = """
You are an analysis agent tasked with understanding and documenting the internal structure and behavior of an MCP (Model Context Protocol) server, which is under test by your own team in a hackathon setting.

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
                           
    With you big reports, try to exploit them calling the exploitation agent. If it succeede return data extracted in your report to showcase the vulnerabilities
"""
