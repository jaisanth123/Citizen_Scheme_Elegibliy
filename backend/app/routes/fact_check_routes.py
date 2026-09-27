from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas.claim import FactCheckRequest, FactCheckResponse
from app.controllers.fact_check_controller import fact_check_controller

router = APIRouter(prefix="/fact-check", tags=["Fact Check"])

@router.post("", response_model=FactCheckResponse)
async def run_fact_check(request: FactCheckRequest):
    """Processes input text through the LangGraph fact-checking pipeline."""
    try:
        return await fact_check_controller.process_fact_check(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def stream_fact_check(request: FactCheckRequest):
    """Streams real-time execution steps and reflection loops via Server-Sent Events."""
    return StreamingResponse(
        fact_check_controller.stream_fact_check(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
