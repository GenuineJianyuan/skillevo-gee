from pathlib import Path
import unittest

from knowledge import KnowledgeCatalog


ROOT = Path(__file__).resolve().parents[1]


class KnowledgeCatalogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog = KnowledgeCatalog(ROOT / "knowledge" / "published")

    def test_published_catalog_is_consistent(self) -> None:
        result = self.catalog.validate()
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["asset_count"], 27)
        self.assertEqual(result["kinds"], {
            "capability": 1,
            "subtask": 19,
            "task": 7,
        })
        self.assertEqual(result["subtasks_without_examples"], [])
        self.assertEqual(result["subtasks_without_example_code"], [])
        self.assertEqual(result["invalid_subtask_structure"], [])
        self.assertEqual(result["invalid_task_structure"], [])
        self.assertEqual(result["invalid_task_operations"], [])
        self.assertEqual(result["invalid_capability_structure"], [])

    def test_search_finds_resampling_task(self) -> None:
        matches = self.catalog.search("Landsat resampling")
        ids = [asset.metadata.id for asset, _ in matches]
        self.assertIn("TASK-IMAGE-RESAMPLING-001", ids)


if __name__ == "__main__":
    unittest.main()

