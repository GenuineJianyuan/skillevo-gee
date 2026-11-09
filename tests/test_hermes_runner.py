from pathlib import Path
import subprocess
import tempfile
from unittest import mock
import unittest

from hermes_runner import HermesRunner


ROOT = Path(__file__).resolve().parents[1]


class HermesRunnerTests(unittest.TestCase):
    @mock.patch("hermes_runner.subprocess.run")
    def test_run_uses_one_shot_hermes_and_direct_client_network(self, run) -> None:
        run.return_value = subprocess.CompletedProcess(
            args=["hermes", "chat"], returncode=0, stdout="done", stderr=""
        )
        runner = HermesRunner(ROOT, executable="hermes")
        result = runner.run("Map seasonal water", timeout_sec=30, status_interval_sec=1)
        self.assertEqual(result, 0)
        args, kwargs = run.call_args
        command = args[0]
        self.assertEqual(command[:2], ["hermes", "chat"])
        self.assertIn("skillevo-alibaba-fast", command)
        self.assertIn("none", command)
        self.assertIn("--max-turns", command)
        self.assertIn("24", command)
        self.assertIn("--run-budget", command)
        self.assertIn("300.0", command)
        self.assertIn("--quiet", command)
        self.assertIn("skillevo-supervisor", command)
        self.assertTrue(command[-1].startswith("Qwen mode directive: /no_think"))
        self.assertIn("Only matched requests", command[-1])
        self.assertIn("autonomous planning and code execution", command[-1])
        self.assertIn("explicit human approval", command[-1])
        self.assertIn("Invoke each state-changing operation once", command[-1])
        self.assertIn("batch catalog retrieval", command[-1])
        self.assertIn("Never inspect or install local plotting", command[-1])
        self.assertEqual(kwargs["env"]["NO_PROXY"], "*")
        self.assertEqual(kwargs["env"]["SKILLEVO_GEE_ROOT"], str(ROOT))
        self.assertTrue(kwargs["capture_output"])
        self.assertTrue(kwargs["text"])
        self.assertEqual(kwargs["encoding"], "utf-8")

    @mock.patch("hermes_runner.subprocess.run")
    def test_show_progress_inherits_console_streams(self, run) -> None:
        run.return_value = subprocess.CompletedProcess(
            args=["hermes", "chat"], returncode=0
        )
        runner = HermesRunner(ROOT, executable="hermes")
        result = runner.run("Map seasonal water", timeout_sec=30, quiet=False)
        self.assertEqual(result, 0)
        command = run.call_args.args[0]
        kwargs = run.call_args.kwargs
        self.assertNotIn("--quiet", command)
        self.assertNotIn("capture_output", kwargs)

    def test_final_response_requires_a_session_id(self) -> None:
        self.assertIsNone(HermesRunner._read_final_response(""))
        self.assertIsNone(HermesRunner._read_final_response("session_id: missing"))

    def test_process_log_has_explicit_success_outcome(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            runner = HermesRunner(Path(directory), executable="hermes")
            relative = runner._write_process_log(
                subprocess.CompletedProcess(["hermes"], 0, "ok", "")
            )
            content = (Path(directory) / relative).read_text(encoding="utf-8")
            self.assertIn("outcome: succeeded", content)
            self.assertIn("success: true", content)
            self.assertIn("exit_code: 0", content)

    def test_process_log_has_explicit_failure_outcome(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            runner = HermesRunner(Path(directory), executable="hermes")
            relative = runner._write_process_log(
                subprocess.CompletedProcess(["hermes"], 1, "", "iteration limit reached")
            )
            content = (Path(directory) / relative).read_text(encoding="utf-8")
            self.assertIn("outcome: failed", content)
            self.assertIn("success: false", content)
            self.assertIn("failure_summary: iteration limit reached", content)


if __name__ == "__main__":
    unittest.main()
