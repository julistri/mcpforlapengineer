
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any
import os
import asyncpg 
import psycopg2

load_dotenv()

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
mcp = FastMCP("lap-engineer", host="0.0.0.0", port=PORT)


# Add a tool to list drivers
@mcp.tool()
def run_drivers_query(query: str) -> dict[str, Any]:
    """
    Führt ein READ-ONLY SELECT-Statement auf der Tabelle driver aus, um Informationen zu Fahrern zu erhalten.

    Rückgabe:
    {
        "rows": [ {col: value, ...}, ... ],
        "row_count": int,
        "columns": [str, ...]
    }
    """
    validate_select_query(query)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()

            data = [dict(zip(columns, row)) for row in rows]

            return {
                "columns": columns,
                "row_count": len(data),
                "rows": data,
            }
    finally:
        conn.close()


# Add a tool to list cars
@mcp.tool()
def run_cars_query(query: str) -> dict[str, Any]:
    """
    Führt ein READ-ONLY SELECT-Statement auf der Tabelle cars aus, um Informationen zu Autos zu erhalten.

    Rückgabe:
    {
        "rows": [ {col: value, ...}, ... ],
        "row_count": int,
        "columns": [str, ...]
    }
    """
    validate_select_query(query)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()

            data = [dict(zip(columns, row)) for row in rows]

            return {
                "columns": columns,
                "row_count": len(data),
                "rows": data,
            }
    finally:
        conn.close() 


# Add a tool to list tracks
@mcp.tool()
def run_tracks_query(query: str) -> dict[str, Any]:
    """
    Führt ein READ-ONLY SELECT-Statement auf der Tabelle track aus, um Informationen zu Strecken zu erhalten.

    Rückgabe:
    {
        "rows": [ {col: value, ...}, ... ],
        "row_count": int,
        "columns": [str, ...]
    }
    """
    validate_select_query(query)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()

            data = [dict(zip(columns, row)) for row in rows]

            return {
                "columns": columns,
                "row_count": len(data),
                "rows": data,
            }
    finally:
        conn.close()         
       

# Add a tool to get the fastest laps
@mcp.tool()
def run_fastestlap_query(query: str) -> dict[str, Any]:
    """
    Führt ein READ-ONLY SELECT-Statement auf der View v_fastest_laps aus, um die schnellsten Runden zu erhalten.

    Rückgabe:
    {
        "rows": [ {col: value, ...}, ... ],
        "row_count": int,
        "columns": [str, ...]
    }
    """
    validate_select_query(query)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()

            data = [dict(zip(columns, row)) for row in rows]

            return {
                "columns": columns,
                "row_count": len(data),
                "rows": data,
            }
    finally:
        conn.close()

# Add a tool to get the avg lap times
@mcp.tool()
def run_avg_lap_time_query(query: str) -> dict[str, Any]:
    """
    Führt ein READ-ONLY SELECT-Statement auf der View v_avg_lap_time aus, um die durchschnittlichen Rundenzeiten zu erhalten.

    Rückgabe:
    {
        "rows": [ {col: value, ...}, ... ],
        "row_count": int,
        "columns": [str, ...]
    }
    """
    validate_select_query(query)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()

            data = [dict(zip(columns, row)) for row in rows]

            return {
                "columns": columns,
                "row_count": len(data),
                "rows": data,
            }
    finally:
        conn.close()


# Frei wählbares SELECT-Statement
@mcp.tool()
def run_select_query(query: str) -> list[dict]:
    """
    Führt ein frei wählbares SELECT-Statement aus (READ ONLY).
     Rückgabe:
    {
        "rows": [ {col: value, ...}, ... ],
        "row_count": int,
        "columns": [str, ...]
    }
    """
    validate_select_query(query)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()

            data = [dict(zip(columns, row)) for row in rows]

            return {
                "columns": columns,
                "row_count": len(data),
                "rows": data,
            }
    finally:
        conn.close()   
    

# a function to validate that the query is a safe SELECT statement
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



# Run the server
if __name__ == "__main__":
    mcp.run(transport="streamable-http")