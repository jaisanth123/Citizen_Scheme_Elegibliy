from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from typing import List, Dict, Any, Optional
from app.controllers.archive_controller import archive_controller

router = APIRouter(prefix="/archive", tags=["Archive & Sources"])

@router.get("/claims", response_model=List[Dict[str, Any]])
def get_claims(
    query: Optional[str] = None,
    verdict: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Retrieves saved claims using the MCP get_saved_claims tool."""
    return archive_controller.get_claims(query=query, verdict=verdict, limit=limit, offset=offset)

@router.get("/claims/{claim_id}/export")
def export_claim(claim_id: str):
    """Exports an individual claim fact-check report as Markdown via MCP."""
    result = archive_controller.export_claim(claim_id)
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result.get("message"))
    return FileResponse(
        path=result["file_path"],
        filename=result["file_name"],
        media_type="text/markdown"
    )

@router.get("/sources", response_model=List[Dict[str, Any]])
def get_trusted_sources():
    """Returns the trusted sources knowledge base registry with credibility and bias notes."""
    return archive_controller.get_trusted_sources()
