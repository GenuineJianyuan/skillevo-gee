import importlib.util
from pathlib import Path
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
            ["skillevo_catalog", "skillevo_workflow_init", "skillevo_gee_execute"],
        )
        result = context.tools[0]["handler"]({"operation": "validate"})
        self.assertIn('"asset_count": 23', result)


if __name__ == "__main__":
    unittest.main()

