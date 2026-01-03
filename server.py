
from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any
import os
import asyncpg 
import psycopg2

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
def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_DATABASE,
        user=DB_USER,
        password=DB_PASSWORD,
    )

pool: Optional[asyncpg.Pool] = None
async def get_pool() -> asyncpg.Pool:
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(DB_CONFIG)
    return pool

# Create an MCP server
mcp = FastMCP("web-search", host="0.0.0.0", port=PORT)

# Add a tool to list all drivers
@mcp.tool(
    name="get_drivers",
    description="Liest alle Einträge aus der Tabelle driver"
)
def get_drivers() -> list[dict]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM driver;")
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()

            return [
                dict(zip(columns, row))
                for row in rows
            ]
    finally:
        conn.close()
       
# Add a tool that executes SQL queries
def validate_select_query(query: str):
    q = query.strip().lower()

    if not q.startswith("select"):
        raise ValueError("Nur SELECT-Statements sind erlaubt")

    forbidden = [
        ";", "--", "/*", "*/",
        "insert", "update", "delete",
        "drop", "alter", "truncate",
        "create", "grant", "revoke"
    ]

    for word in forbidden:
        if word in q:
            raise ValueError(f"Verbotenes SQL-Element erkannt: {word}")

@mcp.tool()
def run_select_query(query: str) -> list[dict]:
    """
    Führt ein frei wählbares SELECT-Statement aus (READ ONLY).
    """
    validate_select_query(query)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            return [dict(zip(columns, row)) for row in rows]
    finally:
        conn.close()       
    



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