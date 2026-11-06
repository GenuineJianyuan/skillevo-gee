from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess


_PROXY_ENV_KEYS = (
    "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY",
    "http_proxy", "https_proxy", "all_proxy",
)


class HermesRunner:
    def __init__(self, project_root: Path, executable: str | None = None):
        self.project_root = project_root.resolve()
        self.executable = executable or shutil.which("hermes")
        if not self.executable:
            raise FileNotFoundError("Hermes executable was not found on PATH")

    def run(
        self,
        request: str,
        reasoning: str = "none",
        timeout_sec: float = 900,
    ) -> int:
        prompt = (
            "Use the SkillEvo-GEE workflow to complete this geospatial analysis request. "
            "Start by normalizing and persisting the requirement, check published capability "
            "coverage using only capabilities.md, and classify it as matched, partial, or "
            "unmatched. Only matched requests may follow Task links to Subtasks. Defer partial "
            "or unmatched requests to pending autonomous planning without using current Task, "
            "Subtask, or Example knowledge. For matched requests, use only Examples embedded in "
            "selected Subtasks, include all required operations and only justified optional "
            "operations, verify data, create a plan before code, execute supported GEE code, "
            "and audit the result. Keep capability gaps and scientific limitations explicit.\n\n"
            f"User request:\n{request}"
        )
        env = os.environ.copy()
        for key in _PROXY_ENV_KEYS:
            env.pop(key, None)
        env["NO_PROXY"] = "*"
        env["no_proxy"] = "*"
        env["SKILLEVO_GEE_ROOT"] = str(self.project_root)
        command = [
            self.executable,
            "chat",
            "--reasoning", reasoning,
            "-s", "skillevo-supervisor",
            "-q", prompt,
        ]
        completed = subprocess.run(
            command,
            cwd=self.project_root,
            env=env,
            timeout=timeout_sec,
            check=False,
        )
        return completed.returncode

