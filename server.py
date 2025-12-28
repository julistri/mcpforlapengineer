# server.py

from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
from typing import Dict

# Initialize Tavily client with your API key
# Replace "TAVILY_API_KEY" with your actual key
tavily_client = TavilyClient("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")

# Create an MCP server named "mcpLapengineer"
mcp = FastMCP("mcpLapengineer", host="0.0.0.0", port=8000)

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