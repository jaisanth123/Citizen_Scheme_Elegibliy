import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List
from app.core.config import DATA_DIR
from app.core.database import get_db_connection
from app.schemas.claim import FactCheckRequest
from app.controllers.fact_check_controller import fact_check_controller
from app.schemas.evaluation import EvalBenchmarkReport, EvalResultItem, EvalTestCase

logger = logging.getLogger("factcheck.eval_controller")

class EvalController:
    def get_test_cases(self) -> List[EvalTestCase]:
        eval_file = DATA_DIR / "eval_claims.json"
        if not eval_file.exists():
            return []
        with open(eval_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [EvalTestCase(**item) for item in data]

    async def run_benchmark(self) -> EvalBenchmarkReport:
        test_cases = self.get_test_cases()
        results: List[EvalResultItem] = []
        correct_count = 0
        unverifiable_guarded_count = 0
        unverifiable_target_count = 0
        
        category_stats: Dict[str, Dict[str, int]] = {}

        for tc in test_cases:
            cat = tc.category
            if cat not in category_stats:
                category_stats[cat] = {"total": 0, "correct": 0}
            category_stats[cat]["total"] += 1
            
            # Run claim through pipeline
            req = FactCheckRequest(text=tc.claim, check_live_web=True, max_reflections=1, topic=tc.category)
            resp = await fact_check_controller.process_fact_check(req)
            
            if resp.results:
                res = resp.results[0]
                pred = res.verdict
                conf = res.confidence
                rounds = res.reflection_rounds
            else:
                pred = "Unverifiable"
                conf = 0.5
                rounds = 0

            # Compare with ground truth
            is_correct = (pred.lower() == tc.ground_truth_verdict.lower())
            if is_correct:
                correct_count += 1
                category_stats[cat]["correct"] += 1

            # Check guardrail adherence
            if tc.ground_truth_verdict.lower() == "unverifiable":
                unverifiable_target_count += 1
                if pred.lower() == "unverifiable":
                    unverifiable_guarded_count += 1

            results.append(EvalResultItem(
                id=tc.id,
                claim=tc.claim,
                ground_truth=tc.ground_truth_verdict,
                predicted_verdict=pred,
                confidence=conf,
                is_correct=is_correct,
                rationale=tc.rationale,
                reflection_rounds=rounds,
                unverifiable_guarded=(pred.lower() == "unverifiable")
            ))

        total = len(test_cases)
        accuracy = (correct_count / total * 100) if total > 0 else 0.0
        guard_rate = (unverifiable_guarded_count / unverifiable_target_count * 100) if unverifiable_target_count > 0 else 100.0

        per_cat = {
            k: round((v["correct"] / v["total"] * 100) if v["total"] > 0 else 0.0, 1)
            for k, v in category_stats.items()
        }

        run_id = f"eval-{uuid.uuid4().hex[:8]}"
        now_str = datetime.utcnow().isoformat() + "Z"

        report = EvalBenchmarkReport(
            run_id=run_id,
            timestamp=now_str,
            total_claims=total,
            correct_count=correct_count,
            accuracy_percentage=round(accuracy, 1),
            unverifiable_guardrail_rate=round(guard_rate, 1),
            per_category_accuracy=per_cat,
            results=results
        )

        # Record run in database
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO eval_runs (id, timestamp, total_claims, correct_count, accuracy, unverifiable_adherence, results_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                run_id,
                now_str,
                total,
                correct_count,
                accuracy,
                guard_rate,
                report.model_dump_json()
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"Could not persist eval run: {e}")

        return report

eval_controller = EvalController()
