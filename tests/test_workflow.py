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

    def test_defers_capability_request_to_pending_queue(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = WorkflowStore(Path(directory))
            state, _ = store.initialize(initialize_requirement("Unsupported analysis"))
            state = store.transition(state, WorkflowStage.CAPABILITY)

            deferred, queue_path = store.defer_to_autonomous_planning(
                state, "No published capability matches the complete objective"
            )

            self.assertEqual(deferred.stage, WorkflowStage.PENDING_AUTONOMOUS_PLANNING)
            self.assertEqual(
                deferred.routing_reason,
                "No published capability matches the complete objective",
            )
            self.assertTrue(queue_path.is_file())
            self.assertEqual(store.load(state.request.request_id), deferred)

    def test_rejects_deferral_before_capability_stage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = WorkflowStore(Path(directory))
            state, _ = store.initialize(initialize_requirement("Unsupported analysis"))
            with self.assertRaises(ValueError):
                store.defer_to_autonomous_planning(state, "not classified")


if __name__ == "__main__":
    unittest.main()

