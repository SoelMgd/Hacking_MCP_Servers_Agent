from smolagents import CodeAgent, Tool

from prompts.auditor_prompts import SYSTEM_PROMPT


@tool
def sent_request_to_mcp(query:str)-> str: 
    """A tool that query the MCP server using the text query and return the response.
    Args:
        query: the query to send to the MCP server
    """

    return "What magic will you build ?"


vulnerability_assessor_agent = CodeAgent(
    system_prompt=SYSTEM_PROMPT,
    tools=[],
    managed_agents=[],
    name="Vulnerability Assessor"
)

