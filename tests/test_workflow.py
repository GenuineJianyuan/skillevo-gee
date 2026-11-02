from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest

from models import FailureClass, WorkflowStage
from workflow import WorkflowStore, initialize_requirement


class WorkflowStoreTests(unittest.TestCase):
    def test_transition_and_failure_routing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = WorkflowStore(Path(directory))
            state, _ = store.initialize(initialize_requirement("Map water", "AOI", "2020"))
            state = store.transition(state, WorkflowStage.CAPABILITY)
            self.assertEqual(state.stage, WorkflowStage.CAPABILITY)
            failed = store.route_failure(state, FailureClass.USER_INPUT, "asset required")
            self.assertEqual(failed.stage, WorkflowStage.AWAITING_USER)

    def test_rejects_invalid_transition(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = WorkflowStore(Path(directory))
            state, _ = store.initialize(initialize_requirement("Map water"))
            with self.assertRaises(ValueError):
                store.transition(state, WorkflowStage.CODE)


if __name__ == "__main__":
    unittest.main()

