import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from app.core.config import settings, EXPORTS_DIR
from app.core.database import get_db_connection

def save_digest(topic: str, date_str: str, markdown_content: str, title: Optional[str] = None, claim_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """MCP tool: Saves a compiled digest with date and topic."""
    digest_id = f"digest-{uuid.uuid4().hex[:8]}"
    if not title:
        title = f"Daily Fact-Check Digest: {topic} ({date_str})"
    if claim_ids is None:
        claim_ids = []
    created_at = datetime.utcnow().isoformat() + "Z"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO saved_digests (id, title, topic, date_str, claim_count, claim_ids, markdown_content, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        digest_id,
        title,
        topic,
        date_str,
        len(claim_ids),
        json.dumps(claim_ids),
        markdown_content,
        created_at
    ))
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "digest_id": digest_id,
        "title": title,
        "topic": topic,
        "date_str": date_str,
        "claim_count": len(claim_ids),
        "created_at": created_at
    }

def get_saved_claims(query: Optional[str] = None, verdict: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """MCP tool: Returns previously checked claims and their verdicts."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql = """
    SELECT id, raw_input, claim_text, verdict, confidence, summary, category, topic,
           supporting_evidence, contradicting_evidence, sources, critic_reflections, reflection_rounds, created_at
    FROM saved_claims
    WHERE 1=1
    """
    params = []
    
    if verdict and verdict.lower() != "all":
        sql += " AND LOWER(verdict) = LOWER(?)"
        params.append(verdict)
        
    if query:
        sql += " AND (claim_text LIKE ? OR summary LIKE ? OR raw_input LIKE ?)"
        pattern = f"%{query}%"
        params.extend([pattern, pattern, pattern])
        
    sql += " ORDER BY datetime(created_at) DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "raw_input": r["raw_input"],
            "claim_text": r["claim_text"],
            "verdict": r["verdict"],
            "confidence": r["confidence"],
            "summary": r["summary"],
            "category": r["category"],
            "topic": r["topic"],
            "supporting_evidence": json.loads(r["supporting_evidence"]) if r["supporting_evidence"] else [],
            "contradicting_evidence": json.loads(r["contradicting_evidence"]) if r["contradicting_evidence"] else [],
            "sources": json.loads(r["sources"]) if r["sources"] else [],
            "critic_reflections": json.loads(r["critic_reflections"]) if r["critic_reflections"] else [],
            "reflection_rounds": r["reflection_rounds"],
            "created_at": r["created_at"]
        })
    return results

def export_markdown(target_type: str, item_id: str) -> Dict[str, Any]:
    """MCP tool: Exports a digest or fact-check report to a Markdown file."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    target_type = target_type.lower()
    file_path = None
    file_content = ""
    title = ""
    
    if target_type == "digest":
        cursor.execute("SELECT id, title, topic, date_str, markdown_content FROM saved_digests WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return {"status": "error", "message": f"Digest with ID {item_id} not found"}
        title = row["title"]
        file_content = row["markdown_content"]
        filename = f"digest_{row['topic'].lower().replace(' ', '_')}_{row['date_str']}_{item_id}.md"
        file_path = EXPORTS_DIR / filename
        
    elif target_type == "claim":
        cursor.execute("""
        SELECT id, claim_text, verdict, confidence, summary, topic, supporting_evidence, contradicting_evidence, sources, created_at
        FROM saved_claims WHERE id = ?
        """, (item_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return {"status": "error", "message": f"Claim with ID {item_id} not found"}
        
        sup = json.loads(row["supporting_evidence"]) if row["supporting_evidence"] else []
        con = json.loads(row["contradicting_evidence"]) if row["contradicting_evidence"] else []
        src = json.loads(row["sources"]) if row["sources"] else []
        
        sup_md = "\n".join([f"- **{e.get('title', 'Source')}** ({e.get('domain', '')}): {e.get('snippet', '')}\n  [Link]({e.get('url', '#')})" for e in sup]) or "_No supporting evidence found._"
        con_md = "\n".join([f"- **{e.get('title', 'Source')}** ({e.get('domain', '')}): {e.get('snippet', '')}\n  [Link]({e.get('url', '#')})" for e in con]) or "_No contradicting evidence found._"
        src_md = "\n".join([f"- [{s.get('title', s.get('domain', 'Link'))}]({s.get('url', '#')}) (Credibility: {int(s.get('credibility_score', 0.8)*100)}%)" for s in src]) or "_No citations listed._"
        
        file_content = f"""# Fact Check Report: {row['verdict'].upper()}
**Claim ID**: `{row['id']}`  
**Verified On**: {row['created_at']}  
**Topic**: {row['topic']}  

---

## 🔍 Verified Proposition
> **"{row['claim_text']}"**

## ⚖️ Official Verdict: `{row['verdict']}`
- **Confidence Rating**: {int(row['confidence'] * 100)}%
- **Executive Summary**: {row['summary']}

---

## 📋 Dual-Sided Evidence Analysis

### Supporting Evidence
{sup_md}

### Contradicting Evidence
{con_md}

---

## 🔗 Authoritative Sources & Citations
{src_md}

---
*Report generated by Veritas Misinformation Fact-Checking Pipeline with LangGraph & MCP.*
"""
        filename = f"factcheck_{item_id}.md"
        file_path = EXPORTS_DIR / filename
        title = f"Fact Check Report: {item_id}"
    else:
        conn.close()
        return {"status": "error", "message": f"Invalid target_type '{target_type}'. Must be 'digest' or 'claim'"}
        
    conn.close()
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(file_content)
        
    return {
        "status": "success",
        "file_name": file_path.name,
        "file_path": str(file_path),
        "content_length": len(file_content),
        "title": title,
        "content": file_content
    }
