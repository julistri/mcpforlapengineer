
from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any
import os
import asyncpg 

# Tavily API key and Tavily client
load_dotenv()
if "TAVILY_API_KEY" not in os.environ:
    raise Exception("TAVILY_API_KEY environment variable not set")
  
TAVILY_API_KEY = os.environ["TAVILY_API_KEY"]
tavily_client = TavilyClient(TAVILY_API_KEY)

PORT = os.environ.get("PORT", 10000)

# Database configuration
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_DATABASE = os.environ["DB_DATABASE"]
DB_CONFIG = {
    "host":  DB_HOST,
    "port": DB_PORT,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "database": DB_DATABASE,
}   
pool: Optional[asyncpg.Pool] = None
async def get_pool() -> asyncpg.Pool:
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(DB_CONFIG)
    return pool

# Create an MCP server
mcp = FastMCP("web-search", host="0.0.0.0", port=PORT)

# Add a tool to list all drivers
@mcp.tool()
async def get_drivers(query: str) -> List[Dict]:
    """
    List all drivers in table driver(read-only).
    """
    pool = await get_pool()

    query = """
        SELECT name, steamname
        FROM driver
        ORDER BY name DESC
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)
        return [dict(row) for row in rows]
# Add a tool for database queries 
@mcp.tool()
async def database_query(query: str) -> List[Dict]:
    """
    Use this tool to query the database.
    """
    pool = await get_pool()

    forbidden = ["insert", "update", "delete", "drop", "alter", "truncate"]
    if any(word in sql.lower() for word in forbidden):
        raise ValueError("Nur SELECT-Abfragen sind erlaubt")

    async with pool.acquire() as conn:
        rows = await conn.fetch(sql)
        return [dict(row) for row in rows]
    
# Add a tool that uses Tavily
@mcp.tool()
def web_search(query: str) -> List[Dict]:
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
    except Exception as e:
        return "Error: " + str(e)

# Run the server
if __name__ == "__main__":
    mcp.run(transport="streamable-http")