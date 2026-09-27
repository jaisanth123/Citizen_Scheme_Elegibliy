import logging
from typing import Dict, Any, List, Optional
from app.mcp.tools import get_saved_claims, export_markdown
from app.services.rag_service import rag_service

logger = logging.getLogger("factcheck.archive_controller")

class ArchiveController:
    def get_claims(self, query: Optional[str] = None, verdict: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        return get_saved_claims(query=query, verdict=verdict, limit=limit, offset=offset)

    def export_claim(self, claim_id: str) -> Dict[str, Any]:
        return export_markdown(target_type="claim", item_id=claim_id)

    def get_trusted_sources(self) -> List[Dict[str, Any]]:
        return rag_service.get_all_trusted_sources()

archive_controller = ArchiveController()
