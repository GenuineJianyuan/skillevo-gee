import unittest

from pydantic import ValidationError

from models import AssetKind, AssetStatus, KnowledgeMetadata


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


if __name__ == "__main__":
    unittest.main()

