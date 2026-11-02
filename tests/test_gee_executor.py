import json
from pathlib import Path
import subprocess
import tempfile
from unittest import mock
import unittest

from gee import GEEExecutor


class GEEExecutorTests(unittest.TestCase):
    @mock.patch("gee.executor.subprocess.run")
    def test_uses_project_runtime_and_explicit_proxy(self, run) -> None:
        run.return_value = subprocess.CompletedProcess([], 0, "", "")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            runtime = root / "src" / "gee" / "runtime"
            runtime.mkdir(parents=True)
            (runtime / "worker.js").write_text("", encoding="utf-8")
            for dependency in ("@google/earthengine", "https-proxy-agent"):
                manifest = runtime / "node_modules" / dependency / "package.json"
                manifest.parent.mkdir(parents=True, exist_ok=True)
                manifest.write_text("{}", encoding="utf-8")

            key = root / "external-key.json"
            key.write_text("{}", encoding="utf-8")
            config = root / "gee.local.json"
            config.write_text(json.dumps({
                "ee_project": "test-project",
                "node_executable": "node",
                "node_service_account_key_path": str(key),
                "proxy_url": "http://127.0.0.1:7890",
            }), encoding="utf-8")
            script = root / "generated.js"
            script.write_text("print(ee.Number(1));", encoding="utf-8")
            output = root / "result.json"
            output.write_text(json.dumps({
                "status": "success",
                "cloud_success_count": 1,
                "cloud_failure_count": 0,
            }), encoding="utf-8")

            record = GEEExecutor(root, config).execute(script, output)

        command = run.call_args.args[0]
        kwargs = run.call_args.kwargs
        self.assertEqual(command[:2], ["node", str(runtime / "worker.js")])
        self.assertIn("http://127.0.0.1:7890", command)
        self.assertEqual(kwargs["cwd"], runtime)
        self.assertNotIn("HTTPS_PROXY", kwargs["env"])
        self.assertEqual(record.cloud_success_count, 1)


if __name__ == "__main__":
    unittest.main()
