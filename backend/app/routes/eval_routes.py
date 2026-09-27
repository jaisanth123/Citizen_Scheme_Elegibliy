from fastapi import APIRouter
from typing import List
from app.schemas.evaluation import EvalBenchmarkReport, EvalTestCase
from app.controllers.eval_controller import eval_controller

router = APIRouter(prefix="/eval", tags=["Evaluation Benchmark"])

@router.get("/dataset", response_model=List[EvalTestCase])
def get_benchmark_dataset():
    """Returns the pre-labelled test cases for fact-checking evaluation."""
    return eval_controller.get_test_cases()

@router.post("/run", response_model=EvalBenchmarkReport)
async def run_benchmark():
    """Runs the fact-checking pipeline across the benchmark dataset and outputs performance metrics."""
    return await eval_controller.run_benchmark()
