import importlib.util
from pathlib import Path
from unittest import mock
import unittest


ROOT = Path(__file__).resolve().parents[1]


class FakeContext:
    def __init__(self) -> None:
        self.tools = []

    def register_tool(self, **kwargs) -> None:
        self.tools.append(kwargs)

    def session_cwd(self) -> str:
        return str(ROOT)


class PluginRegistrationTests(unittest.TestCase):
    def test_declared_tools_register(self) -> None:
        path = ROOT / ".hermes" / "plugins" / "skillevo-gee" / "__init__.py"
        spec = importlib.util.spec_from_file_location("skillevo_gee_hermes_plugin", path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        context = FakeContext()
        module.register(context)
        self.assertEqual(
            [tool["name"] for tool in context.tools],
            [
                "skillevo_catalog",
                "skillevo_workflow_init",
                "skillevo_audit",
                "skillevo_evolution",
                "skillevo_gee_execute",
            ],
        )
        with mock.patch.object(module, "_run", return_value='{"ok": true}') as run:
            context.tools[0]["handler"]({"operation": "validate"})
            self.assertEqual(run.call_args.args[1], ["catalog", "validate"])

            workflow_tool = context.tools[1]
            workflow_tool["handler"]({
                "operation": "init",
                "objective": "Map seasonal water area",
            })
            self.assertEqual(
                run.call_args.args[1],
                ["workflow", "init", "--objective", "Map seasonal water area"],
            )
            workflow_tool["handler"]({
                "operation": "defer",
                "request_id": "req-test",
                "reason": "Only part of the objective matches published capabilities",
            })
            self.assertEqual(run.call_args.args[1][:4], [
                "workflow", "defer", "--request-id", "req-test",
            ])


if __name__ == "__main__":
    unittest.main()

