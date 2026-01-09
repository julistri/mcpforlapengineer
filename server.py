
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


# Add a tool to list all cars
@mcp.tool(
    name="get_cars",
    description="Liest alle Einträge aus der Tabelle cars"
)

def get_cars() -> list[dict]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM cars;")
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()

            return [
                dict(zip(columns, row))
                for row in rows
            ]
    finally:
        conn.close()   


# Add a tool to list all tracks
@mcp.tool(
    name="get_tracks",
    description="Liest alle Einträge aus der Tabelle tracks"
)

def get_tracks() -> list[dict]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM track;")
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()

            return [
                dict(zip(columns, row))
                for row in rows
            ]
    finally:
        conn.close()             
       

# Add a tool to list fastest GT3 laps per track
@mcp.tool(
    name="get_fastest_GT3_laps",
    description="Liest alle Einträge aus der View fastest_GT3_laps_per_track"
)

def get_fastest_GT3_laps() -> list[dict]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM fastest_GT3_laps_per_track;")
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()

            return [
                dict(zip(columns, row))
                for row in rows
            ]
    finally:
        conn.close() 


# Add a tool to list fastest LMP2 laps per track
@mcp.tool(
    name="get_fastest_LMP2_laps",
    description="Liest alle Einträge aus der View fastest_LMP2_laps_per_track"
)

def get_fastest_LMP2_laps() -> list[dict]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM fastest_LMP2_laps_per_track;")
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()

            return [
                dict(zip(columns, row))
                for row in rows
            ]
    finally:
        conn.close() 

# Add a tool to list fastest Hypercar laps per track
@mcp.tool(
    name="get_fastest_Hypercar_laps",
    description="Liest alle Einträge aus der View fastest_Hypercar_laps_per_track"
)

def get_fastest_Hypercar_laps() -> list[dict]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM fastest_Hypercar_laps_per_track;")
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()

            return [
                dict(zip(columns, row))
                for row in rows
            ]
    finally:
        conn.close() 


# Add a tool to list fastest GTE laps per track
@mcp.tool(
    name="get_fastest_GTE_laps",
    description="Liest alle Einträge aus der View fastest_GTE_laps_per_track"
)

def get_fastest_GTE_laps() -> list[dict]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM fastest_GTE_laps_per_track;")
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()

            return [
                dict(zip(columns, row))
                for row in rows
            ]
    finally:
        conn.close() 


# Add a tool to list fastest LMP3 laps per track
@mcp.tool(
    name="get_fastest_LMP3_laps",
    description="Liest alle Einträge aus der View fastest_LMP3_laps_per_track"
)

def get_fastest_LMP3_laps() -> list[dict]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM fastest_LMP3_laps_per_track;")
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

# Frei wählbares SELECT-Statement
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
    

# Run the server
if __name__ == "__main__":
    mcp.run(transport="streamable-http")