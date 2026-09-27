from typing import TypedDict, List, Dict, Any, Optional

class FactCheckState(TypedDict):
    raw_input: str
    topic: Optional[str]
    check_live_web: bool
    max_reflections: int
    current_reflection_round: int
    
    # Extracted Claims
    claims: List[Dict[str, Any]]
    
    # Evidence Gathered (keyed by claim id)
    evidences: Dict[str, Dict[str, Any]]
    
    # Verdicts (keyed by claim id)
    verdicts: Dict[str, Dict[str, Any]]
    
    # Critic feedback (keyed by claim id)
    critic_feedbacks: Dict[str, List[Dict[str, Any]]]
    
    # Reflection queries to run in next iteration
    pending_queries: Dict[str, List[str]]
    
    # Audit log / progression steps for frontend live visualization
    step_logs: List[Dict[str, Any]]
    
    # Status: 'in_progress', 'completed', 'error'
    status: str
    error: Optional[str]
