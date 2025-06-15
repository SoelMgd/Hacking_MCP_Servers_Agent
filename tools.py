from smolagents import tool
import requests

@tool
def sent_request_to_mcp(query:str)-> str: 
    """A tool that query the MCP server using the text query and return the response.
    Args:
        query: the query to send to the MCP server
    """
    url = "http://127.0.0.1:8000/mcp"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": query
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()
