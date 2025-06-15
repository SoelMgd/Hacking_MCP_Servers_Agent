from smolagents import LiteLLMModel, tool
from typing import Optional
from agents.orchestrator import orchestrator_agent
import os

from dotenv import load_dotenv
load_dotenv()


model = LiteLLMModel(model_id="claude-sonnet-4-20250514",
                     api_key=os.getenv("ANTHROPIC_API_KEY"))


@tool
def my_custom_tool(arg1:str, arg2:int)-> str: # it's important to specify the return type
    # Keep this format for the tool description / args description but feel free to modify the tool
    """A tool that does nothing yet 
    Args:
        arg1: the first argument
        arg2: the second argument
    """
    return "What magic will you build ?"


orchestrator = orchestrator_agent(tools=[], model=model)
answer = orchestrator.run("Please try to find vulnearibilites of this MCP server and exploit them.")
print(answer)