from smolagents import tool
import requests
import os

MCP_API_URL = os.getenv("MCP_API_URL", "https://jdelavande-hack-me-mcp.hf.space/mcp")

@tool
def sent_request_to_mcp(query:str, url:str=MCP_API_URL) -> str:
    """A tool that query MCP server using natural language.
    This function sends a query to the MCP server and returns the response.
    Args:
        query: the query to send to the MCP server
        url: the URL of the MCP server (default is set via environment variable MCP_API_URL)
    Returns:
        str: The response from the MCP server
    """
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": query
    }
    
    response = requests.post(url, headers=headers, json=data)

    return response.json()


