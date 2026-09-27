import re
import uuid
import logging
from typing import Dict, Any, List
from app.agents.state import FactCheckState
from app.core.llm import llm_client

logger = logging.getLogger("factcheck.claim_extractor")

SYSTEM_PROMPT = """You are a senior investigative fact-checker and claim extraction agent.
Your mission is to read input text (forwarded messages, social media posts, news statements) and extract individual, discrete, checkable factual assertions.
Ignore polite greetings, generic rhetoric, and personal opinions that cannot be verified empirically.
For each factual assertion, formulate a clear, declarative claim statement.

Output JSON with this schema:
{
  "claims": [
    {
      "claim_text": "Declarative factual claim",
      "category": "Health | Technology | Science | Politics | Society | General",
      "checkable": true
    }
  ]
}
"""

async def claim_extractor_node(state: FactCheckState) -> Dict[str, Any]:
    raw_input = state["raw_input"].strip()
    logger.info(f"Extracting claims from input: {raw_input[:60]}...")
    
    user_prompt = f"Extract checkable factual claims from the following text:\n\n\"{raw_input}\""
    
    def deterministic_fallback() -> Dict[str, Any]:
        cleaned = re.sub(r'^(forwarded message:?|is it true that|fact-check this:?|please verify:?)\s*', '', raw_input, flags=re.IGNORECASE).strip()
        cleaned = cleaned.rstrip('?')
        
        # Split compound sentences or multiple lines
        lines = [line.strip() for line in raw_input.split('\n') if len(line.strip()) > 15]
        
        # Determine category
        cat = "General"
        low = raw_input.lower()
        if any(w in low for w in ["water", "cure", "virus", "infection", "vaccine", "doctor", "health", "cancer"]):
            cat = "Health"
        elif any(w in low for w in ["tech", "ai", "quantum", "5g", "computer", "algorithm", "software"]):
            cat = "Technology"
        elif any(w in low for w in ["nasa", "space", "planet", "astronomy", "telescope", "physics"]):
            cat = "Science"
        elif any(w in low for w in ["unesco", "anthem", "law", "government", "election", "court"]):
            cat = "Society"
            
        claims_list = []
        if len(lines) > 1 and not lines[0].lower().startswith("is it true"):
            for line in lines[:3]:
                line_clean = re.sub(r'^[•\-\*\d\.]+\s*', '', line).strip()
                if len(line_clean) > 15:
                    claims_list.append({
                        "claim_text": line_clean,
                        "category": cat,
                        "checkable": True
                    })
        
        if not claims_list:
            claims_list.append({
                "claim_text": cleaned if len(cleaned) > 10 else raw_input,
                "category": cat,
                "checkable": True
            })
            
        return {"claims": claims_list}

    try:
        response = await llm_client.generate_json(
            prompt=user_prompt,
            system_prompt=SYSTEM_PROMPT,
            fallback_func=deterministic_fallback
        )
        extracted = response.get("claims", [])
        if not extracted:
            extracted = deterministic_fallback()["claims"]
    except Exception as e:
        logger.warning(f"LLM claim extraction failed ({e}), using fallback.")
        extracted = deterministic_fallback()["claims"]

    claims_with_id = []
    for idx, c in enumerate(extracted):
        claims_with_id.append({
            "id": f"claim-{idx+1}-{uuid.uuid4().hex[:4]}",
            "claim_text": c.get("claim_text", raw_input),
            "category": c.get("category", "General"),
            "checkable": c.get("checkable", True)
        })

    step_log = {
        "node": "claim_extractor",
        "description": f"Extracted {len(claims_with_id)} testable proposition(s)",
        "details": [c["claim_text"] for c in claims_with_id],
        "reflection_round": state.get("current_reflection_round", 0)
    }

    return {
        "claims": claims_with_id,
        "step_logs": state.get("step_logs", []) + [step_log]
    }
