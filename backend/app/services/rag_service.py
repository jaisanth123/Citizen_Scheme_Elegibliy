import json
import logging
import re
from typing import List, Dict, Any, Optional
from app.core.database import get_db_connection

logger = logging.getLogger("factcheck.rag")

class RAGService:
    def __init__(self):
        self._trusted_sources_cache: Dict[str, Dict[str, Any]] = {}
        self._load_trusted_sources()

    def _load_trusted_sources(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trusted_sources'")
            if not cursor.fetchone():
                conn.close()
                return
            cursor.execute("SELECT domain, name, credibility_score, bias_rating, category, notes FROM trusted_sources")
            rows = cursor.fetchall()
            for r in rows:
                self._trusted_sources_cache[r["domain"].lower()] = {
                    "domain": r["domain"],
                    "name": r["name"],
                    "credibility_score": r["credibility_score"],
                    "bias_rating": r["bias_rating"],
                    "category": r["category"],
                    "notes": r["notes"]
                }
            conn.close()
        except Exception as e:
            logger.debug(f"Trusted sources cache not loaded yet: {e}")

    def get_source_credibility(self, domain: str) -> Dict[str, Any]:
        """Looks up a domain in the trusted source registry."""
        d = domain.lower().replace("www.", "")
        if d in self._trusted_sources_cache:
            return self._trusted_sources_cache[d]
        
        # Check subdomains or parent domains
        for known_domain, info in self._trusted_sources_cache.items():
            if d.endswith("." + known_domain) or known_domain.endswith("." + d):
                return info
                
        # Default unverified domain score
        return {
            "domain": domain,
            "name": domain.capitalize(),
            "credibility_score": 0.70,
            "bias_rating": "Unknown / Unrated",
            "category": "Web Source",
            "notes": "Domain not yet evaluated in the trusted source index."
        }

    def search_archive(self, query: str, limit: int = 3, threshold: float = 0.25) -> List[Dict[str, Any]]:
        """Searches previously verified claims archive using word-overlap and token matching."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, raw_input, claim_text, verdict, confidence, summary, category, 
                   supporting_evidence, contradicting_evidence, sources, created_at
            FROM saved_claims
            """)
            rows = cursor.fetchall()
            conn.close()

            q_tokens = set(re.findall(r'\b\w{3,}\b', query.lower()))
            if not q_tokens:
                return []

            matched = []
            for r in rows:
                text_corpus = f"{r['claim_text']} {r['summary']} {r['raw_input']}".lower()
                c_tokens = set(re.findall(r'\b\w{3,}\b', text_corpus))
                
                intersection = q_tokens.intersection(c_tokens)
                if not intersection:
                    continue
                    
                score = len(intersection) / max(len(q_tokens), 1)
                if score >= threshold:
                    matched.append({
                        "id": r["id"],
                        "claim_text": r["claim_text"],
                        "verdict": r["verdict"],
                        "confidence": r["confidence"],
                        "summary": r["summary"],
                        "category": r["category"],
                        "similarity_score": round(score, 3),
                        "sources": json.loads(r["sources"]) if r["sources"] else [],
                        "created_at": r["created_at"]
                    })

            matched.sort(key=lambda x: x["similarity_score"], reverse=True)
            return matched[:limit]
        except Exception as e:
            logger.warning(f"Archive search error: {e}")
            return []

    def get_all_trusted_sources(self) -> List[Dict[str, Any]]:
        if not self._trusted_sources_cache:
            self._load_trusted_sources()
        return list(self._trusted_sources_cache.values())

rag_service = RAGService()
