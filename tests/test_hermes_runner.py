from pathlib import Path
from unittest import mock
import unittest

from hermes_runner import HermesRunner


ROOT = Path(__file__).resolve().parents[1]


class HermesRunnerTests(unittest.TestCase):
    @mock.patch("hermes_runner.subprocess.run")
    def test_run_uses_one_shot_hermes_and_direct_client_network(self, run) -> None:
        run.return_value.returncode = 0
        runner = HermesRunner(ROOT, executable="hermes")
        result = runner.run("Map seasonal water", timeout_sec=30)
        self.assertEqual(result, 0)
        args, kwargs = run.call_args
        command = args[0]
        self.assertEqual(command[:2], ["hermes", "chat"])
        self.assertIn("skillevo-supervisor", command)
        self.assertIn("Only matched requests", command[-1])
        self.assertIn("pending autonomous planning", command[-1])
        self.assertEqual(kwargs["env"]["NO_PROXY"], "*")
        self.assertEqual(kwargs["env"]["SKILLEVO_GEE_ROOT"], str(ROOT))


if __name__ == "__main__":
    unittest.main()
