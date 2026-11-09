import unittest
from datetime import datetime, timezone

from pydantic import ValidationError

from models import (
    AssetKind,
    AssetStatus,
    AuditRecommendation,
    AuditReport,
    KnowledgeMetadata,
)


class KnowledgeMetadataTests(unittest.TestCase):
    def test_rejects_unstable_lowercase_id(self) -> None:
        with self.assertRaises(ValidationError):
            KnowledgeMetadata(
                id="task-one",
                kind=AssetKind.TASK,
                title="Task",
                version="1.0.0",
                status=AssetStatus.DRAFT,
                summary="Summary",
            )

    def test_rejects_candidate_eligibility_when_audit_gate_fails(self) -> None:
        with self.assertRaises(ValidationError):
            AuditReport(
                request_id="req-test",
                execution_passed=True,
                data_passed=False,
                plan_passed=True,
                acceptance_passed=True,
                candidate_eligible=True,
                recommendation=AuditRecommendation.ADD,
                audited_at=datetime.now(timezone.utc),
            )


if __name__ == "__main__":
    unittest.main()

