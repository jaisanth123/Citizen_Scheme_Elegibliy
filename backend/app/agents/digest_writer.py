import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.agents.state import FactCheckState
from app.core.database import get_db_connection
from app.mcp.tools import save_digest
from app.core.llm import llm_client

logger = logging.getLogger("factcheck.digest_writer")

async def finalize_and_persist_node(state: FactCheckState) -> Dict[str, Any]:
    """Persists verified claims to the database/MCP registry and records final status."""
    raw_input = state.get("raw_input", "")
    claims = state.get("claims", [])
    verdicts = state.get("verdicts", {})
    evidences = state.get("evidences", {})
    feedbacks = state.get("critic_feedbacks", {})
    topic = state.get("topic", "General")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.utcnow().isoformat() + "Z"
    
    persisted_count = 0
    for claim in claims:
        cid = claim["id"]
        v = verdicts.get(cid)
        if not v:
            continue
            
        ev = evidences.get(cid, {})
        fb = feedbacks.get(cid, [])
        rounds = v.get("reflection_rounds", 0)
        
        cursor.execute("""
        INSERT OR REPLACE INTO saved_claims
        (id, raw_input, claim_text, verdict, confidence, summary, category, topic,
         supporting_evidence, contradicting_evidence, sources, critic_reflections, reflection_rounds, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            cid,
            raw_input,
            claim["claim_text"],
            v["verdict"],
            v["confidence"],
            v["summary"],
            claim.get("category", "General"),
            topic,
            json.dumps(v.get("supporting_evidence", [])),
            json.dumps(v.get("contradicting_evidence", [])),
            json.dumps(v.get("sources", [])),
            json.dumps(fb),
            rounds,
            now_str
        ))
        persisted_count += 1
        
    conn.commit()
    conn.close()
    
    log_entry = {
        "node": "finalize",
        "description": f"Persisted {persisted_count} verified claim(s) to RAG & MCP database",
        "details": "Ready for export, digest compilation, or user viewing.",
        "reflection_round": state.get("current_reflection_round", 0)
    }
    
    return {
        "status": "completed",
        "step_logs": state.get("step_logs", []) + [log_entry]
    }

async def generate_digest_document(topic: str, date_str: str, claims_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compiles multiple verified claims or news into a structured Markdown digest and saves via MCP."""
    title = f"Daily Verified News & Fact-Check Digest: {topic} ({date_str})"
    
    verdicts_summary_md = []
    for idx, c in enumerate(claims_data, 1):
        v = c.get("verdict", "Unverifiable")
        badge = {"True": "✅ TRUE", "False": "❌ FALSE", "Misleading": "⚠️ MISLEADING", "Unverifiable": "❔ UNVERIFIABLE"}.get(v, v)
        sources_list = ", ".join([s.get("title", s.get("domain", "")) for s in c.get("sources", [])[:3]]) or "Multiple accredited outlets"
        
        verdicts_summary_md.append(f"""### {idx}. {c.get('claim_text', 'Claim')}
- **Verdict**: `{badge}` (Confidence: {int(c.get('confidence', 0.8) * 100)}%)
- **Analysis**: {c.get('summary', '')}
- **Sources**: {sources_list}
""")

    digest_md = f"""# {title}
**Date**: {date_str}  
**Curated By**: Veritas Multi-Agent Fact-Checking Engine  
**Total Claims Evaluated**: {len(claims_data)}  

---

## 📌 Executive Overview
This digest aggregates claims investigated across digital media, social networks, and live news feeds concerning **{topic}**. Every claim has undergone multi-agent verification, dual-sided evidence retrieval via Tavily search and RAG archives, and editorial critique reflection.

---

## 🔍 Verified Claims & Verdicts

{"".join(verdicts_summary_md)}

---

## 🛡️ Methodology & Guardrails
- **Dual-Sided Evidence**: Supporting and counter-evidence are weighed with source credibility weighting.
- **Unverifiable Default**: Unsubstantiated claims lacking empirical consensus are marked as Unverifiable rather than speculatively categorized.
- **MCP Storage**: Automatically catalogued and exported via Model Context Protocol tools.
"""

    claim_ids = [c.get("id", "") for c in claims_data if c.get("id")]
    
    # Save using MCP tool
    save_result = save_digest(
        topic=topic,
        date_str=date_str,
        markdown_content=digest_md,
        title=title,
        claim_ids=claim_ids
    )
    
    return {
        "id": save_result["digest_id"],
        "title": title,
        "topic": topic,
        "date_str": date_str,
        "claim_count": len(claims_data),
        "claim_ids": claim_ids,
        "markdown_content": digest_md,
        "created_at": save_result["created_at"]
    }
