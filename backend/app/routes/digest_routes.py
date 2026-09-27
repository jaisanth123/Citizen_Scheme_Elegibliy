from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from typing import List, Dict, Any
from app.schemas.digest import DigestRequest, DigestResponse
from app.controllers.digest_controller import digest_controller

router = APIRouter(prefix="/digest", tags=["Daily Digest"])

@router.post("/generate", response_model=DigestResponse)
async def generate_digest(request: DigestRequest):
    """Compiles verified claims into a daily digest document and stores via MCP."""
    try:
        return await digest_controller.create_digest(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list", response_model=List[Dict[str, Any]])
async def list_digests(limit: int = 20):
    """Returns past compiled fact-check digests."""
    return await digest_controller.list_digests(limit=limit)

@router.get("/{digest_id}/export")
async def export_digest(digest_id: str):
    """Exports and downloads the digest markdown file via MCP."""
    result = await digest_controller.export_digest_markdown(digest_id)
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result.get("message"))
    return FileResponse(
        path=result["file_path"],
        filename=result["file_name"],
        media_type="text/markdown"
    )
