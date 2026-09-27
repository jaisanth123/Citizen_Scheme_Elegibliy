import logging
from typing import Dict, Any, List
from app.agents.state import FactCheckState
from app.core.llm import llm_client
from app.core.config import settings

logger = logging.getLogger("factcheck.verdict_judge")

SYSTEM_PROMPT = """You are an impartial, highly rigorous Verdict Judge adhering to International Fact-Checking Network (IFCN) standards.
Your role is to weigh all supporting and contradicting evidence for each claim and assign a verdict:
- 'True': Factual proposition is thoroughly substantiated by high-credibility primary records or authoritative scientific consensus.
- 'False': Factual proposition directly contradicts empirical evidence, authoritative findings, or official records.
- 'Misleading': Contains elements of truth but distorted, omitted crucial context, or exaggerated beyond reality.
- 'Unverifiable': CRITICAL GUARDRAIL: If evidence is sparse, vague, from unverified rumors, or genuine scientific consensus is lacking, you MUST output 'Unverifiable' rather than guess.

Provide a balanced, completely unbiased summary citing why the evidence points to this verdict, noting evidence from both perspectives.

Output JSON format:
{
  "verdict": "True | False | Misleading | Unverifiable",
  "confidence": 0.95,
  "summary": "Clear, objective, balanced explanation..."
}
"""

async def verdict_judge_node(state: FactCheckState) -> Dict[str, Any]:
    claims = state.get("claims", [])
    evidences = state.get("evidences", {})
    verdicts = state.get("verdicts", {}).copy()
    round_num = state.get("current_reflection_round", 0)
    
    logger.info(f"Verdict Judge evaluating {len(claims)} claim(s) (Round {round_num})")
    
    new_logs = []
    
    for claim in claims:
        cid = claim["id"]
        ctext = claim["claim_text"]
        claim_ev = evidences.get(cid, {})
        
        sup_items = claim_ev.get("supporting", [])
        con_items = claim_ev.get("contradicting", [])
        rag_items = claim_ev.get("rag_matches", [])
        
        # Calculate credibility-weighted scores
        sup_weight = sum(item.get("credibility_score", 0.7) for item in sup_items)
        con_weight = sum(item.get("credibility_score", 0.7) for item in con_items)
        
        # Check if RAG has an exact or high match
        rag_override = None
        if rag_items and rag_items[0].get("similarity_score", 0) >= 0.65:
            rag_match = rag_items[0]
            rag_override = {
                "verdict": rag_match["verdict"],
                "confidence": max(rag_match["confidence"], 0.95),
                "summary": rag_match["summary"]
            }

        def deterministic_evaluation() -> Dict[str, Any]:
            if rag_override:
                return rag_override
                
            total_evidence_count = len(sup_items) + len(con_items)
            
            # Guardrail: If almost no evidence was found, or text is absurdly vague rumor without dates/names
            if total_evidence_count == 0 or (sup_weight < 0.8 and con_weight < 0.8):
                return {
                    "verdict": "Unverifiable",
                    "confidence": 0.40,
                    "summary": f"Insufficient verifiable empirical evidence or accredited reporting found to substantiate or disprove this assertion. Guardrail enforced: rated Unverifiable rather than speculating."
                }
                
            # If both strong support and strong contradiction with near parity -> Misleading
            if sup_weight > 1.2 and con_weight > 1.2:
                ratio = min(sup_weight, con_weight) / max(sup_weight, con_weight)
                if ratio > 0.5:
                    return {
                        "verdict": "Misleading",
                        "confidence": 0.82,
                        "summary": "Evidence shows elements of factual basis mixed with significant conflicting claims or omitted context, presenting a distorted impression."
                    }
                    
            if con_weight > sup_weight * 1.5:
                conf = min(0.98, 0.75 + (con_weight * 0.08))
                return {
                    "verdict": "False",
                    "confidence": round(conf, 2),
                    "summary": f"Authoritative documentation, official agency clarifications, and peer-reviewed evidence contradict this claim. There is no verified corroboration."
                }
            elif sup_weight > con_weight * 1.5:
                conf = min(0.98, 0.75 + (sup_weight * 0.08))
                return {
                    "verdict": "True",
                    "confidence": round(conf, 2),
                    "summary": f"Substantiated by verified publications, primary scientific instruments, or official organizational records."
                }
            else:
                return {
                    "verdict": "Misleading",
                    "confidence": 0.78,
                    "summary": f"The proposition presents partial truths or oversimplifications that do not accurately convey the complete evidentiary consensus."
                }

        # Compose prompt for LLM
        prompt_text = f"""Claim: "{ctext}"

Supporting Evidence:
{sup_items}

Contradicting Evidence:
{con_items}

RAG Matched Fact Checks:
{rag_items}
"""
        try:
            llm_result = await llm_client.generate_json(
                prompt=prompt_text,
                system_prompt=SYSTEM_PROMPT,
                fallback_func=deterministic_evaluation
            )
            verdict_val = llm_result.get("verdict", "Unverifiable")
            if verdict_val not in ["True", "False", "Misleading", "Unverifiable"]:
                verdict_val = "Unverifiable"
            confidence_val = float(llm_result.get("confidence", 0.70))
            summary_val = llm_result.get("summary", "")
        except Exception as e:
            logger.warning(f"LLM verdict judge error ({e}), using deterministic evaluation.")
            fallback = deterministic_evaluation()
            verdict_val = fallback["verdict"]
            confidence_val = fallback["confidence"]
            summary_val = fallback["summary"]

        verdicts[cid] = {
            "id": cid,
            "claim_text": ctext,
            "verdict": verdict_val,
            "confidence": confidence_val,
            "summary": summary_val,
            "supporting_evidence": sup_items,
            "contradicting_evidence": con_items,
            "sources": claim_ev.get("sources", []),
            "topic": claim.get("category", "General"),
            "reflection_rounds": round_num
        }

        new_logs.append({
            "node": "verdict_judge",
            "description": f"Assigned verdict for '{ctext[:40]}...': {verdict_val} ({int(confidence_val*100)}% confidence)",
            "details": summary_val[:120] + "...",
            "reflection_round": round_num
        })

    return {
        "verdicts": verdicts,
        "step_logs": state.get("step_logs", []) + new_logs
    }
