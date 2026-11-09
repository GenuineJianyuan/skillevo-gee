from datetime import datetime, timezone
from pathlib import Path
import shutil
import tempfile
import unittest

from evolution import CandidateStore
from models import (
    AuditRecommendation,
    AuditReport,
    CandidateStatus,
    EvolutionOperation,
)


ROOT = Path(__file__).resolve().parents[1]


class CandidateStoreTests(unittest.TestCase):
    def _root_with_audited_run(self, directory: str) -> tuple[Path, str]:
        root = Path(directory)
        shutil.copytree(ROOT / "knowledge" / "published", root / "knowledge" / "published")
        request_id = "req-test"
        run = root / "runs" / request_id
        run.mkdir(parents=True)
        audit = AuditReport(
            request_id=request_id,
            execution_passed=True,
            data_passed=True,
            plan_passed=True,
            acceptance_passed=True,
            candidate_eligible=True,
            recommendation=AuditRecommendation.MODIFY,
            findings=["Validated correction"],
            evidence_paths=["runs/req-test/execution.json"],
            audited_at=datetime.now(timezone.utc),
        )
        (run / "audit.json").write_text(audit.model_dump_json(indent=2), encoding="utf-8")
        return root, request_id

    def test_modify_requires_approval_before_publish(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, request_id = self._root_with_audited_run(directory)
            store = CandidateStore(root)
            targets = [
                "TASK-IMAGE-RESAMPLING-001",
                "SUBTASK-IMAGE-RESAMPLE-001",
            ]
            candidate, candidate_dir = store.create(
                request_id=request_id,
                operation=EvolutionOperation.MODIFY,
                recommendation=AuditRecommendation.MODIFY,
                rationale="Regression-tested clarification",
                source_refs=["runs/req-test/audit.json"],
                target_asset_ids=targets,
                evidence=[],
            )
            proposed = candidate_dir / "proposed"
            shutil.copy2(root / "knowledge" / "published" / "capabilities.md", proposed / "capabilities.md")
            shutil.copy2(
                root / "knowledge" / "published" / "tasks" / "TASK-IMAGE-RESAMPLING-001.md",
                proposed / "tasks" / "TASK-IMAGE-RESAMPLING-001.md",
            )
            shutil.copy2(
                root / "knowledge" / "published" / "subtasks" / "SUBTASK-IMAGE-RESAMPLE-001.md",
                proposed / "subtasks" / "SUBTASK-IMAGE-RESAMPLE-001.md",
            )

            validated = store.validate(candidate.candidate_id)
            self.assertEqual(validated.status, CandidateStatus.AWAITING_APPROVAL)
            with self.assertRaises(PermissionError):
                store.publish(candidate.candidate_id)
            store.approve(candidate.candidate_id, "human-reviewer")
            published = store.publish(candidate.candidate_id)
            self.assertEqual(published.status, CandidateStatus.PUBLISHED)


if __name__ == "__main__":
    unittest.main()
