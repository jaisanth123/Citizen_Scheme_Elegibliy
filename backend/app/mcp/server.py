"""MCP Server exposing save_digest, get_saved_claims, and export_markdown."""
import os
import sys
import json
from mcp.server.fastmcp import FastMCP
from app.mcp.tools import save_digest, get_saved_claims, export_markdown

# Initialize FastMCP Server
mcp_server = FastMCP("Veritas Fact-Check MCP Server")

@mcp_server.tool()
def mcp_save_digest(topic: str, date_str: str, markdown_content: str, title: str = "") -> str:
    """Saves a compiled digest with date and topic to the database.
    
    Args:
        topic: The topic of the digest (e.g. Technology, Health).
        date_str: Date string in YYYY-MM-DD.
        markdown_content: Formatted markdown content of the digest.
        title: Optional title for the digest.
    """
    res = save_digest(topic=topic, date_str=date_str, markdown_content=markdown_content, title=title)
    return json.dumps(res, indent=2)

@mcp_server.tool()
def mcp_get_saved_claims(query: str = "", verdict: str = "", limit: int = 50) -> str:
    """Returns previously checked claims and their verdicts.
    
    Args:
        query: Optional text search string.
        verdict: Optional verdict filter ('True', 'False', 'Misleading', 'Unverifiable').
        limit: Max claims to return (default: 50).
    """
    res = get_saved_claims(query=query if query else None, verdict=verdict if verdict else None, limit=limit)
    return json.dumps(res, indent=2)

@mcp_server.tool()
def mcp_export_markdown(target_type: str, item_id: str) -> str:
    """Exports a digest or fact-check report to a Markdown file on disk.
    
    Args:
        target_type: Either 'digest' or 'claim'.
        item_id: The unique identifier of the digest or claim.
    """
    res = export_markdown(target_type=target_type, item_id=item_id)
    return json.dumps(res, indent=2)

if __name__ == "__main__":
    mcp_server.run()
