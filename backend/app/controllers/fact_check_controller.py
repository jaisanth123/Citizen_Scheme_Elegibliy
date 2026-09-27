import json
import logging
from datetime import datetime
from typing import AsyncGenerator, Dict, Any, List
from app.agents.graph import fact_check_app
from app.schemas.claim import FactCheckRequest, FactCheckResponse, ClaimVerdict, EvidenceItem, SourceItem

logger = logging.getLogger("factcheck.controller")

class FactCheckController:
    async def process_fact_check(self, req: FactCheckRequest) -> FactCheckResponse:
        initial_state = {
            "raw_input": req.text,
            "topic": req.topic or "General",
            "check_live_web": req.check_live_web,
            "max_reflections": req.max_reflections,
            "current_reflection_round": 0,
            "claims": [],
            "evidences": {},
            "verdicts": {},
            "critic_feedbacks": {},
            "pending_queries": {},
            "step_logs": [],
            "status": "in_progress",
            "error": None
        }

        final_state = await fact_check_app.ainvoke(initial_state)
        
        results: List[ClaimVerdict] = []
        for c in final_state.get("claims", []):
            cid = c["id"]
            v = final_state.get("verdicts", {}).get(cid, {})
            fb = final_state.get("critic_feedbacks", {}).get(cid, [])
            
            critic_summary = None
            if fb:
                critic_summary = f"Round {fb[-1].get('round', 1)}: {fb[-1].get('reason')}"
                
            results.append(ClaimVerdict(
                id=cid,
                claim_text=c.get("claim_text", req.text),
                verdict=v.get("verdict", "Unverifiable"),
                confidence=v.get("confidence", 0.5),
                summary=v.get("summary", "Analysis completed."),
                supporting_evidence=[EvidenceItem(**item) for item in v.get("supporting_evidence", [])],
                contradicting_evidence=[EvidenceItem(**item) for item in v.get("contradicting_evidence", [])],
                sources=[SourceItem(**item) for item in v.get("sources", [])],
                critic_notes=critic_summary,
                reflection_rounds=v.get("reflection_rounds", 0),
                topic=req.topic or c.get("category", "General"),
                created_at=datetime.utcnow().isoformat() + "Z"
            ))

        return FactCheckResponse(
            id=f"check-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            raw_input=req.text,
            timestamp=datetime.utcnow().isoformat() + "Z",
            total_claims=len(results),
            results=results
        )

    async def stream_fact_check(self, req: FactCheckRequest) -> AsyncGenerator[str, None]:
        """Streams real-time step events as the LangGraph pipeline and reflection nodes execute."""
        initial_state = {
            "raw_input": req.text,
            "topic": req.topic or "General",
            "check_live_web": req.check_live_web,
            "max_reflections": req.max_reflections,
            "current_reflection_round": 0,
            "claims": [],
            "evidences": {},
            "verdicts": {},
            "critic_feedbacks": {},
            "pending_queries": {},
            "step_logs": [],
            "status": "in_progress",
            "error": None
        }

        # Yield pipeline started event
        yield json.dumps({
            "event": "started",
            "message": "Fact-checking pipeline initialized. Invoking Claim Extractor...",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }) + "\n\n"

        try:
            # Stream node updates from LangGraph
            async for output in fact_check_app.astream(initial_state):
                for node_name, state_patch in output.items():
                    logs = state_patch.get("step_logs", [])
                    latest_log = logs[-1] if logs else {"node": node_name, "description": f"Executed {node_name}"}
                    
                    event_payload = {
                        "event": "node_update",
                        "node": node_name,
                        "description": latest_log.get("description", ""),
                        "details": latest_log.get("details", ""),
                        "reflection_round": latest_log.get("reflection_round", 0),
                        "claims": state_patch.get("claims"),
                        "verdicts": state_patch.get("verdicts"),
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    }
                    yield json.dumps(event_payload) + "\n\n"

            # Final complete response event
            full_res = await self.process_fact_check(req)
            yield json.dumps({
                "event": "finished",
                "data": full_res.model_dump(),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }) + "\n\n"

        except Exception as e:
            logger.error(f"Error streaming fact-check: {e}")
            yield json.dumps({
                "event": "error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }) + "\n\n"

fact_check_controller = FactCheckController()
