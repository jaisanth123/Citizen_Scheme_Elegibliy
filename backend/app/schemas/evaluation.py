from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class EvalTestCase(BaseModel):
    id: str
    claim: str
    ground_truth_verdict: str
    category: str
    difficulty: str
    rationale: str

class EvalResultItem(BaseModel):
    id: str
    claim: str
    ground_truth: str
    predicted_verdict: str
    confidence: float
    is_correct: bool
    rationale: str
    reflection_rounds: int
    unverifiable_guarded: bool

class EvalBenchmarkReport(BaseModel):
    run_id: str
    timestamp: str
    total_claims: int
    correct_count: int
    accuracy_percentage: float
    unverifiable_guardrail_rate: float
    per_category_accuracy: Dict[str, float]
    results: List[EvalResultItem]
