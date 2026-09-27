import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.schemas.digest import DigestRequest, DigestResponse
from app.agents.digest_writer import generate_digest_document
from app.mcp.tools import get_saved_claims, export_markdown
from app.core.database import get_db_connection

logger = logging.getLogger("factcheck.digest_controller")

class DigestController:
    async def create_digest(self, req: DigestRequest) -> DigestResponse:
        date_str = req.date_str or datetime.utcnow().strftime("%Y-%m-%d")
        
        # 1. Fetch claims to compile
        claims_to_include = []
        if req.claim_ids:
            all_saved = get_saved_claims(limit=100)
            claims_to_include = [c for c in all_saved if c["id"] in req.claim_ids]
        else:
            # Query relevant claims by topic or get recent
            all_saved = get_saved_claims(query=req.topic if req.topic != "All" else None, limit=10)
            if not all_saved:
                all_saved = get_saved_claims(limit=5)
            claims_to_include = all_saved

        if not claims_to_include:
            # If no claims saved yet, provide a placeholder claim
            claims_to_include = [{
                "id": "notice-01",
                "claim_text": f"Recent developments and reports regarding {req.topic}",
                "verdict": "Unverifiable",
                "confidence": 0.5,
                "summary": "No verified claims catalogued yet for this category.",
                "sources": []
            }]

        digest_doc = await generate_digest_document(
            topic=req.topic,
            date_str=date_str,
            claims_data=claims_to_include
        )

        return DigestResponse(
            id=digest_doc["id"],
            title=digest_doc["title"],
            topic=digest_doc["topic"],
            date_str=digest_doc["date_str"],
            claim_count=digest_doc["claim_count"],
            claim_ids=digest_doc["claim_ids"],
            markdown_content=digest_doc["markdown_content"],
            created_at=digest_doc["created_at"]
        )

    async def list_digests(self, limit: int = 20) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT id, title, topic, date_str, claim_count, claim_ids, markdown_content, created_at
        FROM saved_digests ORDER BY datetime(created_at) DESC LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()

        digests = []
        for r in rows:
            digests.append({
                "id": r["id"],
                "title": r["title"],
                "topic": r["topic"],
                "date_str": r["date_str"],
                "claim_count": r["claim_count"],
                "claim_ids": json.loads(r["claim_ids"]) if r["claim_ids"] else [],
                "markdown_content": r["markdown_content"],
                "created_at": r["created_at"]
            })
        return digests

    async def export_digest_markdown(self, digest_id: str) -> Dict[str, Any]:
        return export_markdown(target_type="digest", item_id=digest_id)

digest_controller = DigestController()
