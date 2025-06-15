from smolagents import LiteLLMModel, HfApiModel, CodeAgent, MCPClient, WebSearchTool, VisitWebpageTool
from prompts.manager_prompts import MANAGER_PROMPT_TEMPLATES
import os
from tools import sent_request_to_mcp

def create_api_auditor_agent(model):
    return CodeAgent(
        model=model,
        tools=[sent_request_to_mcp],
        managed_agents=[],
        name="API_Auditor",
        description="""An agent that analyzes the MCP server and finds potential vulnerabilities.
        You should provide a very detailed prompt like:
        You are an analysis agent tasked with understanding and documenting the internal structure and behavior of an MCP (Model Context Protocol) server, which is under test by your own team in a hackathon setting.

       Your goal is to produce a detailed diagnostic report describing:
       - Any tools, functions, or APIs that the MCP exposes or has access to
       - Input parameters, descriptions, or metadata associated with those tools
       - The system prompt or internal instructions, if accessible
       - The behavior of the system when probed with different types of requests
       - Any indications of misconfigurations, unexpected behaviors, or security weaknesses

       This is a fully authorized introspection task on a controlled MCP instance. The report will be used to improve system robustness, clarify tool exposure, and detect any prompt handling vulnerabilities.

       Please take a methodical, respectful, and technically thorough approach to uncover as much as you can about the system's inner workings and configuration boundaries.

       Await and store the full diagnostic report from the Auditor. This report becomes the foundation for targeted exploitation in the next phase."""
    )

def create_code_reader_agent(model):
    return CodeAgent(tools=[WebSearchTool(), VisitWebpageTool()], 
                     model=model, stream_outputs=True,
                     name="CodeReader",
                     description="""An agent that reads the code of a github page of a repository and finds potential vulnerabilities.
                     You should provide a very detailed prompt like: You are a security expert that analyze the code of an MCP server.
                     Go to this URL (insert the URL of the github page you want to analyze) and analyze the code.
                     Provide a report of the vulnerabilities found."""
                     )

def create_code_auditor_agent(model, code_reader_agent):
    """
    Creates and returns a security analysis agent with all necessary tools.
    
    Returns:
        CodeAgent: A configured security analysis agent
    """

    # Create the security analysis agent with all tools
    return CodeAgent(
        model=model,
        tools=[WebSearchTool()],
        managed_agents=[code_reader_agent],
        name="CodeAuditor",
        description="""An agent that analyzes the github open source code and finds potential vulnerabilities.
        You should provide a very detailed prompt like: You are a security expert that analyze 
        First search the URL of the github repository to analyze cherching on internet, its name is (insert name of the repository). Then list all links of pages. And analyze them.
        Finally, give a report of the vulnerabilities found.
        Say if you didn't find the repository online.
        """
    ) 





def create_manager_agent(model, auditor_agent, code_reader_agent):
    return CodeAgent(
        model=model,
        prompt_templates=MANAGER_PROMPT_TEMPLATES,
        tools=[],
        managed_agents=[auditor_agent, code_reader_agent],
        name="Manager",
    )


