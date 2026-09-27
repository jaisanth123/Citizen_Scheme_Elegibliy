import logging
from typing import Dict, Any, List
from app.agents.state import FactCheckState
from app.services.tavily_service import tavily_service
from app.services.rag_service import rag_service

logger = logging.getLogger("factcheck.evidence_retriever")

async def evidence_retriever_node(state: FactCheckState) -> Dict[str, Any]:
    claims = state.get("claims", [])
    evidences = state.get("evidences", {}).copy()
    pending_queries = state.get("pending_queries", {})
    round_num = state.get("current_reflection_round", 0)
    
    logger.info(f"Evidence Retriever running (Round {round_num}) for {len(claims)} claim(s)")
    
    new_logs = []
    
    for claim in claims:
        cid = claim["id"]
        ctext = claim["claim_text"]
        
        # Initialize evidence store for this claim if absent
        if cid not in evidences:
            evidences[cid] = {
                "rag_matches": [],
                "supporting": [],
                "contradicting": [],
                "neutral": [],
                "sources": []
            }
            
        existing_urls = {e.get("url") for e in evidences[cid]["supporting"] + evidences[cid]["contradicting"] + evidences[cid]["neutral"]}
        
        # 1. RAG Archive Search
        archive_results = rag_service.search_archive(ctext, limit=2)
        evidences[cid]["rag_matches"].extend(archive_results)
        
        # 2. Formulate queries: if reflection provided targeted queries, use those; otherwise standard queries
        queries_to_run = []
        if cid in pending_queries and pending_queries[cid]:
            queries_to_run.extend(pending_queries[cid])
        else:
            queries_to_run.append(ctext)
            queries_to_run.append(f"{ctext} fact check debunk")
            queries_to_run.append(f"{ctext} official evidence")

        # 3. Search Tavily / Web
        raw_web_results = []
        for q in queries_to_run[:3]: # Cap queries per claim per round
            results = await tavily_service.search(query=q, max_results=3)
            raw_web_results.extend(results)

        # 4. Classify stance and compute source credibility
        for item in raw_web_results:
            url = item.get("url", "")
            if url in existing_urls:
                continue
            existing_urls.add(url)
            
            domain = item.get("domain", "")
            cred_info = rag_service.get_source_credibility(domain)
            credibility = cred_info.get("credibility_score", 0.80)
            source_name = cred_info.get("name", domain)
            
            snippet = item.get("snippet", "")
            snippet_low = snippet.lower()
            ctext_low = ctext.lower()
            
            # Stance heuristics & keywords
            neg_indicators = ["false", "debunk", "myth", "hoax", "no evidence", "unfounded", "fabricated", "untrue", "refuted", "inaccurate", "misleading", "fake"]
            pos_indicators = ["confirmed", "true", "verified", "evidence shows", "proven", "official statement confirms", "detected", "published in nature", "peer-reviewed"]
            
            neg_count = sum(1 for w in neg_indicators if w in snippet_low)
            pos_count = sum(1 for w in pos_indicators if w in snippet_low)
            
            evidence_entry = {
                "title": item.get("title", "Evidence"),
                "url": url,
                "domain": domain,
                "snippet": snippet,
                "credibility_score": credibility,
                "source_name": source_name,
                "published_date": item.get("published_date")
            }
            
            if neg_count > pos_count:
                evidence_entry["stance"] = "contradict"
                evidences[cid]["contradicting"].append(evidence_entry)
            elif pos_count > neg_count:
                evidence_entry["stance"] = "support"
                evidences[cid]["supporting"].append(evidence_entry)
            else:
                evidence_entry["stance"] = "neutral"
                evidences[cid]["neutral"].append(evidence_entry)
                
            # Track source citation
            evidences[cid]["sources"].append({
                "title": item.get("title", source_name),
                "url": url,
                "domain": domain,
                "credibility_score": credibility
            })

        new_logs.append({
            "node": "evidence_retriever",
            "description": f"Gathered evidence for '{ctext[:40]}...' (Round {round_num})",
            "details": f"Support: {len(evidences[cid]['supporting'])}, Contradict: {len(evidences[cid]['contradicting'])}, RAG matches: {len(evidences[cid]['rag_matches'])}",
            "reflection_round": round_num
        })

    return {
        "evidences": evidences,
        "pending_queries": {}, # Clear executed queries
        "step_logs": state.get("step_logs", []) + new_logs
    }
