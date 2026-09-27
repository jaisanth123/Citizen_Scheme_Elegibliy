from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime

class EvidenceItem(BaseModel):
    title: str
    url: str
    domain: str
    snippet: str
    credibility_score: float = 0.85
    stance: Literal["support", "contradict", "neutral"] = "neutral"
    source_name: Optional[str] = None
    published_date: Optional[str] = None

class SourceItem(BaseModel):
    title: str
    url: str
    domain: str
    credibility_score: float = 0.85

class CriticFeedback(BaseModel):
    needs_more_evidence: bool = False
    reason: str = ""
    suggested_queries: List[str] = []
    bias_warning: Optional[str] = None
    approved: bool = True
    round: int = 1

class ExtractedClaim(BaseModel):
    id: str
    claim_text: str
    category: Optional[str] = "General"
    checkable: bool = True

class ClaimVerdict(BaseModel):
    id: str
    claim_text: str
    verdict: Literal["True", "False", "Misleading", "Unverifiable"]
    confidence: float = Field(ge=0.0, le=1.0)
    summary: str
    supporting_evidence: List[EvidenceItem] = []
    contradicting_evidence: List[EvidenceItem] = []
    sources: List[SourceItem] = []
    critic_notes: Optional[str] = None
    reflection_rounds: int = 0
    topic: Optional[str] = "General"
    created_at: Optional[str] = None

class FactCheckRequest(BaseModel):
    text: str = Field(..., min_length=3, description="Text, forwarded message, or claim to fact check")
    check_live_web: bool = True
    max_reflections: int = 2
    topic: Optional[str] = None

class FactCheckResponse(BaseModel):
    id: str
    raw_input: str
    timestamp: str
    total_claims: int
    results: List[ClaimVerdict]

class SavedClaimFilter(BaseModel):
    query: Optional[str] = None
    verdict: Optional[str] = None
    limit: int = 50
    offset: int = 0
