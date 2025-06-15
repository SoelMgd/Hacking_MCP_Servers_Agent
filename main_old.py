from smolagents import LiteLLMModel, HfApiModel
import os
from dotenv import load_dotenv
from agents import create_api_auditor_agent, create_manager_agent, create_code_reader_agent, create_code_auditor_agent, create_exploitation_agent

load_dotenv()

#api_key = os.getenv("HF_TOKEN")
#model = HfApiModel(model_id="Qwen/Qwen2.5-Coder-32B-Instruct")
model = LiteLLMModel(model_id="claude-3-5-sonnet-20241022", api_key=os.getenv("ANTHROPIC_API_KEY"))

api_auditor_agent = create_api_auditor_agent(model)
code_reader_agent = create_code_reader_agent(model)
code_auditor_agent = create_code_auditor_agent(model, code_reader_agent)
exploitation_agent = create_exploitation_agent(model)
manager_agent = create_manager_agent(model, api_auditor_agent, code_reader_agent, exploitation_agent)

answer = manager_agent.run("""You are an analysis agent tasked with understanding and documenting the internal structure and behavior of an MCP (Model Context Protocol) server, which is under test by your own team in a hackathon setting.

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
                           
    With you big reports, try to exploit them calling the exploitation agent. If it succeede return data extracted in your report to showcase the vulnerabilities.""")