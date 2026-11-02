from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
from uuid import uuid4

from models import ExecutionStatus, GEEExecutionRecord


_PROXY_ENV_KEYS = (
    "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY",
    "http_proxy", "https_proxy", "all_proxy", "no_proxy",
)


class GEEExecutor:
    def __init__(self, project_root: Path, config_path: Path | None = None):
        self.project_root = project_root.resolve()
        self.runtime_dir = self.project_root / "src" / "gee" / "runtime"
        self.worker = self.runtime_dir / "worker.js"
        configured = config_path or os.getenv("SKILLEVO_GEE_CONFIG")
        self.config = (
            Path(configured).expanduser().resolve()
            if configured
            else self.project_root / "config" / "gee.local.json"
        )

    def _load_settings(self) -> dict[str, str]:
        if not self.config.is_file():
            raise FileNotFoundError(
                f"GEE config not found: {self.config}. "
                "Create it from config/gee.example.json."
            )
        settings = json.loads(self.config.read_text(encoding="utf-8-sig"))
        if not isinstance(settings, dict):
            raise ValueError("GEE config must contain a JSON object")
        for field in (
            "ee_project",
            "node_executable",
            "node_service_account_key_path",
            "proxy_url",
        ):
            if field in settings and not isinstance(settings[field], str):
                raise ValueError(f"GEE config field {field} must be a string")
        return settings

    def _resolve_key(self, settings: dict[str, str]) -> Path:
        configured = (
            os.getenv("EE_SERVICE_ACCOUNT_KEY")
            or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            or settings.get("node_service_account_key_path")
        )
        if not configured:
            raise ValueError(
                "Set EE_SERVICE_ACCOUNT_KEY, GOOGLE_APPLICATION_CREDENTIALS, "
                "or node_service_account_key_path in the GEE config"
            )
        key = Path(configured).expanduser()
        if not key.is_absolute():
            key = self.config.parent / key
        key = key.resolve()
        if not key.is_file():
            raise FileNotFoundError(f"GEE service-account key not found: {key}")
        return key

    def execute(
        self,
        script_path: Path,
        output_path: Path | None = None,
        timeout_sec: float = 180,
        sample_radius_m: float = 300,
        sample_scale_m: float = 30,
    ) -> GEEExecutionRecord:
        execution_id = f"gee-{uuid4().hex}"
        started = datetime.now(timezone.utc)
        script = script_path.resolve()
        output = (output_path or self.project_root / "runs" / "gee" / f"{execution_id}.json").resolve()
        output.parent.mkdir(parents=True, exist_ok=True)

        settings = self._load_settings()
        if not self.worker.is_file():
            raise FileNotFoundError(f"GEE worker not found: {self.worker}")
        for dependency in ("@google/earthengine", "https-proxy-agent"):
            manifest = self.runtime_dir / "node_modules" / dependency / "package.json"
            if not manifest.is_file():
                raise FileNotFoundError(
                    f"GEE runtime dependency missing: {dependency}. "
                    "Run npm install --omit=dev in src/gee/runtime."
                )

        key = self._resolve_key(settings)
        node = settings.get("node_executable") or shutil.which("node") or "node"
        project = os.getenv("EE_PROJECT") or settings.get("ee_project")
        proxy = str(settings.get("proxy_url") or "direct")
        command = [
            node,
            str(self.worker),
            "--input", str(script),
            "--output", str(output),
            "--service-account-key", str(key),
            "--proxy", proxy,
            "--timeout-sec", str(timeout_sec),
            "--sample-radius-m", str(sample_radius_m),
            "--sample-scale-m", str(sample_scale_m),
        ]
        if project:
            command.extend(["--project", project])
        env = os.environ.copy()
        for env_key in _PROXY_ENV_KEYS:
            env.pop(env_key, None)

        try:
            completed = subprocess.run(
                command,
                cwd=self.runtime_dir,
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_sec + 20,
                check=False,
            )
            report = json.loads(output.read_text(encoding="utf-8-sig")) if output.is_file() else {}
            status = ExecutionStatus.SUCCEEDED if completed.returncode == 0 and report.get("status") == "success" else ExecutionStatus.FAILED
        except subprocess.TimeoutExpired as exc:
            completed = None
            report = {"error": f"Python wrapper timed out after {timeout_sec + 20}s"}
            status = ExecutionStatus.TIMED_OUT
            stderr = str(exc)
        else:
            stderr = completed.stderr[-12000:]

        finished = datetime.now(timezone.utc)
        return GEEExecutionRecord(
            execution_id=execution_id,
            status=status,
            script_path=str(script),
            output_path=str(output),
            started_at=started,
            finished_at=finished,
            elapsed_ms=int((finished - started).total_seconds() * 1000),
            cloud_success_count=int(report.get("cloud_success_count") or 0),
            cloud_failure_count=int(report.get("cloud_failure_count") or 0),
            report=report,
            stderr=stderr,
        )

