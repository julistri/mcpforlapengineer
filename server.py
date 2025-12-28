# server.py

from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
from dotenv import load_dotenv
from typing import Dict
import os

load_dotenv()
TAVILY_API_KEY = os.environ["TAVILY_API_KEY"]
if "TAVILY_API_KEY" not in os.environ:
    raise Exception("TAVILY_API_KEY environment variable not set")

# Initialize Tavily client with your API key
tavily_client = TavilyClient(TAVILY_API_KEY)

PORT = os.environ.get("PORT", 10000)
# Create an MCP server named "mcpLapengineer"
mcp = FastMCP("mcpLapengineer", host="0.0.0.0", port=PORT)

# Add a tool that uses Tavily for web searches
@mcp.tool()
def web_search(query: str) -> Dict:
    """
    Use this tool to search the web for information.

    Args:
        query: The search query.

    Returns:
        The search results.
    """
    try:
        response = tavily_client.search(query)
        return response["results"]
    except Exception:
        return "No results found"

# Run the server
if __name__ == "__main__":
    mcp.run(transport="streamable-http")