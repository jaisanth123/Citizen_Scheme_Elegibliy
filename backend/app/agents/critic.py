import logging
from typing import Dict, Any, List
from app.agents.state import FactCheckState
from app.core.llm import llm_client

logger = logging.getLogger("factcheck.critic")

SYSTEM_PROMPT = """You are an independent Senior Editorial Critic and Fact-Check Reviewer.
Your duty is to challenge conclusions, audit for media bias, ensure dual-sided evidence representation, and verify source quality.
Review the verdict, confidence score, and supporting vs contradicting evidence for the claim.

If the evidence is one-sided, lacks authoritative sources, or fails to address potential counter-claims, demand further evidence and formulate 1-2 targeted search queries.
If the verdict is sound, well-supported, or already reflects maximum available evidence, approve it.

Output JSON format:
{
  "approved": true | false,
  "reason": "Clear critique rationale...",
  "suggested_queries": ["query 1", "query 2"],
  "bias_warning": null | "Warning note..."
}
"""

async def critic_node(state: FactCheckState) -> Dict[str, Any]:
    claims = state.get("claims", [])
    evidences = state.get("evidences", {})
    verdicts = state.get("verdicts", {})
    critic_feedbacks = state.get("critic_feedbacks", {}).copy()
    current_round = state.get("current_reflection_round", 0)
    max_rounds = state.get("max_reflections", 2)
    
    logger.info(f"Critic reviewing verdicts (Round {current_round}/{max_rounds})")
    
    pending_queries = {}
    new_logs = []
    any_reflection_needed = False
    
    for claim in claims:
        cid = claim["id"]
        ctext = claim["claim_text"]
        v_info = verdicts.get(cid, {})
        ev_info = evidences.get(cid, {})
        
        sup = ev_info.get("supporting", [])
        con = ev_info.get("contradicting", [])
        rag = ev_info.get("rag_matches", [])
        verdict = v_info.get("verdict", "Unverifiable")
        
        if cid not in critic_feedbacks:
            critic_feedbacks[cid] = []

        def deterministic_critique() -> Dict[str, Any]:
            # If maximum rounds reached, approve
            if current_round >= max_rounds:
                return {
                    "approved": True,
                    "reason": f"Maximum reflection depth ({max_rounds}) reached. Finalizing balanced verdict.",
                    "suggested_queries": [],
                    "bias_warning": None
                }
                
            # If high confidence RAG match, instantly approve
            if rag and rag[0].get("similarity_score", 0) >= 0.70:
                return {
                    "approved": True,
                    "reason": "Pre-verified historical fact-check match confirmed from authoritative RAG archive.",
                    "suggested_queries": [],
                    "bias_warning": None
                }
                
            # If claim is "True" but zero contradicting checks were done, request counter-search
            if verdict == "True" and len(con) == 0 and current_round == 0:
                return {
                    "approved": False,
                    "reason": "Verdict is 'True' but lacks dual-sided investigation. Search specifically for credible dissenting analysis or counter-evidence.",
                    "suggested_queries": [f"{ctext} criticisms controversy debunk", f"{ctext} alternative explanations"],
                    "bias_warning": "Potential confirmation bias: verify opposing viewpoints."
                }
                
            # If claim is "False" but zero supporting checks were done, request confirmation search
            if verdict == "False" and len(sup) == 0 and current_round == 0:
                return {
                    "approved": False,
                    "reason": "Verdict is 'False'. Verify if any official agency has issued qualifications, exceptions, or partial confirmations.",
                    "suggested_queries": [f"{ctext} official statement context", f"{ctext} primary source"],
                    "bias_warning": None
                }

            # If total evidence is very sparse (< 2 items)
            if (len(sup) + len(con)) < 2 and current_round == 0:
                return {
                    "approved": False,
                    "reason": "Sparse evidence base. Broaden web and institutional archive search queries.",
                    "suggested_queries": [f"{ctext} Reuters AP News BBC", f"{ctext} official documentation"],
                    "bias_warning": "Low evidence volume."
                }
                
            return {
                "approved": True,
                "reason": "Verdict demonstrates rigorous dual-sided evidentiary evaluation and conforms to guardrails.",
                "suggested_queries": [],
                "bias_warning": None
            }

        # Prompt LLM
        prompt_text = f"""Review this fact-check assessment:
Claim: "{ctext}"
Verdict: {verdict} ({v_info.get('confidence', 0)*100:.0f}% confidence)
Summary: {v_info.get('summary')}
Supporting evidence count: {len(sup)}
Contradicting evidence count: {len(con)}
Current Reflection Round: {current_round} (Max: {max_rounds})
"""
        try:
            critique = await llm_client.generate_json(
                prompt=prompt_text,
                system_prompt=SYSTEM_PROMPT,
                fallback_func=deterministic_critique
            )
            approved = critique.get("approved", True)
            if current_round >= max_rounds:
                approved = True
        except Exception as e:
            logger.warning(f"LLM critic error ({e}), using deterministic critique.")
            critique = deterministic_critique()
            approved = critique.get("approved", True)

        critic_feedbacks[cid].append({
            "round": current_round,
            "approved": approved,
            "reason": critique.get("reason", "Approved"),
            "suggested_queries": critique.get("suggested_queries", []),
            "bias_warning": critique.get("bias_warning")
        })

        if not approved:
            any_reflection_needed = True
            pending_queries[cid] = critique.get("suggested_queries", [])
            new_logs.append({
                "node": "critic",
                "description": f"Critic requested reflection for '{ctext[:40]}...': {critique.get('reason')}",
                "details": f"Triggering targeted evidence retrieval round {current_round + 1} with queries: {critique.get('suggested_queries')}",
                "reflection_round": current_round,
                "action": "reflect"
            })
        else:
            new_logs.append({
                "node": "critic",
                "description": f"Critic approved verdict for '{ctext[:40]}...'",
                "details": critique.get("reason"),
                "reflection_round": current_round,
                "action": "approved"
            })

    next_round = current_round + (1 if any_reflection_needed else 0)

    return {
        "critic_feedbacks": critic_feedbacks,
        "pending_queries": pending_queries,
        "current_reflection_round": next_round,
        "step_logs": state.get("step_logs", []) + new_logs
    }

def should_reflect(state: FactCheckState) -> str:
    """Conditional router function for LangGraph."""
    max_rounds = state.get("max_reflections", 2)
    current_round = state.get("current_reflection_round", 0)
    pending_queries = state.get("pending_queries", {})
    
    # If any claim has pending reflection queries and we haven't reached max rounds
    if pending_queries and any(len(q) > 0 for q in pending_queries.values()) and current_round <= max_rounds:
        logger.info(f"LangGraph conditional route: REFLECT -> evidence_retriever (Round {current_round})")
        return "evidence_retriever"
        
    logger.info("LangGraph conditional route: APPROVE -> persist_and_finalize")
    return "finalize"
