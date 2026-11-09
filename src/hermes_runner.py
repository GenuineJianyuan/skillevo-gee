from __future__ import annotations

import os
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys
import threading
import time
from uuid import uuid4


_PROXY_ENV_KEYS = (
    "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY",
    "http_proxy", "https_proxy", "all_proxy",
)

DEFAULT_PROVIDER = "skillevo-alibaba-fast"
DEFAULT_MAX_TURNS = 24
DEFAULT_RUN_BUDGET_SEC = 300.0

_STAGE_AGENTS = {
    "requirement": "Requirement Agent",
    "capability": "Requirement Agent",
    "knowledge": "Planning Agent",
    "data": "Data Agent",
    "planning": "Planning Agent",
    "code": "Code Agent",
    "execution": "Audit Agent / GEE Executor",
    "audit": "Audit Agent",
    "pending_autonomous_planning": "Supervisor Agent",
    "autonomous_planning": "Planning Agent",
    "candidate_preparation": "Evolution Agent",
    "awaiting_approval": "Evolution Agent",
    "awaiting_user": "Supervisor Agent",
    "completed": "Supervisor Agent",
    "failed": "Supervisor Agent",
}


def agent_for_stage(stage: str) -> str:
    return _STAGE_AGENTS.get(stage, "Supervisor Agent")


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
        provider: str = DEFAULT_PROVIDER,
        max_turns: int = DEFAULT_MAX_TURNS,
        run_budget_sec: float = DEFAULT_RUN_BUDGET_SEC,
        quiet: bool = True,
        status_interval_sec: float = 15.0,
    ) -> int:
        prompt = (
            "Qwen mode directive: /no_think.\n"
            "Execute directly from the preloaded SkillEvo-GEE Skills and published Markdown. "
            "Do not expose chain-of-thought, narrate intermediate reasoning, explore unrelated "
            "files, or redesign a matched published workflow. "
            "Start by normalizing and persisting the requirement, check published capability "
            "coverage using only capabilities.md, and classify it as matched, partial, or "
            "unmatched. Only matched requests may follow Task links to Subtasks. Route partial "
            "or unmatched requests through autonomous planning and code execution without using "
            "current Task, Subtask, or Example knowledge. For matched requests, use only Examples embedded in "
            "selected Subtasks, include all required operations and only justified optional "
            "operations, verify data, create a plan before code, execute supported GEE code, "
            "and audit the result. Save autonomous results under runs and create an Add/Modify "
            "candidate only when audit evidence makes it eligible; never approve or publish "
            "without explicit human approval. Keep capability gaps and scientific limitations explicit. "
            "Invoke each state-changing operation once, follow the legal workflow-stage order, "
            "and retry a failed GEE execution at most once after a concrete correction. Return only "
            "a concise final result; store detailed intermediate evidence under runs. Use batch catalog "
            "retrieval for a Task's referenced Subtasks. Never inspect or install local plotting/Python "
            "packages; no chart-library probe is part of the geospatial workflow. Interpret 'no export' "
            "as no Earth Engine Export task, and keep headless chart limitations explicit. For a matched "
            "request, Planning must use only this request's registered artifacts, write/register one concise "
            "plan in one pass, never inspect historical runs, and transition immediately to Code.\n\n"
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
            "--provider", provider,
            "--reasoning", reasoning,
            "--max-turns", str(max_turns),
            "--run-budget", str(run_budget_sec),
            "-s", "skillevo-supervisor",
        ]
        if quiet:
            command.append("--quiet")
        command += ["-q", prompt]
        run_options = {
            "cwd": self.project_root,
            "env": env,
            "timeout": timeout_sec,
            "check": False,
        }
        if quiet:
            run_options.update(
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        if quiet:
            completed = self._run_with_status(command, run_options, status_interval_sec)
        else:
            completed = subprocess.run(command, **run_options)
        if quiet:
            log_path = self._write_process_log(completed)
            final_response = self._read_final_response(completed.stderr or "")
            if final_response:
                print(final_response.strip())
            if completed.returncode == 0:
                print(
                    f"[SkillEvo-GEE] SUCCESS | Hermes exit: 0 | "
                    f"full process log: {log_path}",
                    flush=True,
                )
            else:
                print(
                    f"[SkillEvo-GEE] FAILED | Hermes exit: {completed.returncode} | "
                    f"full process log: {log_path}",
                    file=sys.stderr,
                    flush=True,
                )
        return completed.returncode

    def _run_with_status(
        self,
        command: list[str],
        run_options: dict[str, object],
        status_interval_sec: float,
    ) -> subprocess.CompletedProcess[str]:
        before = {path.parent.name for path in (self.project_root / "runs").glob("req-*/state.json")}
        result: dict[str, object] = {}

        def invoke() -> None:
            try:
                result["completed"] = subprocess.run(command, **run_options)
            except BaseException as exc:
                result["error"] = exc

        started = time.monotonic()
        worker = threading.Thread(target=invoke, name="hermes-runner", daemon=True)
        print("[SkillEvo-GEE] Agent: Supervisor Agent | stage: starting | launching Hermes", flush=True)
        worker.start()

        request_id: str | None = None
        state_path: Path | None = None
        last_stage: str | None = None
        last_artifacts: set[str] = set()
        next_heartbeat = started + max(status_interval_sec, 1.0)
        while worker.is_alive():
            if state_path is None:
                states = self._new_workflow_states(before)
                if states:
                    # Bind to the first request created by this invocation.
                    # Requests from another concurrent CLI must not replace or
                    # repeatedly warn in this monitor.
                    state_path = states[0]
            if state_path is not None:
                request_id = state_path.parent.name
                state = self._load_state(state_path)
                if state:
                    stage = str(state.get("stage", "unknown"))
                    artifacts = set((state.get("artifact_paths") or {}).keys())
                    if stage != last_stage:
                        direction = "stage"
                        if last_stage and self._stage_index(stage) < self._stage_index(last_stage):
                            direction = f"local rollback from {last_stage}"
                        print(
                            f"[SkillEvo-GEE] Agent: {agent_for_stage(stage)} "
                            f"| {direction}: {stage} | request: {request_id}",
                            flush=True,
                        )
                        last_stage = stage
                    new_artifacts = artifacts - last_artifacts
                    if new_artifacts:
                        print(
                            f"[SkillEvo-GEE] artifacts ready: {', '.join(sorted(new_artifacts))}",
                            flush=True,
                        )
                    last_artifacts = artifacts
            now = time.monotonic()
            if now >= next_heartbeat:
                stage = last_stage or "initializing"
                agent = agent_for_stage(stage)
                suffix = f" | request: {request_id}" if request_id else ""
                print(
                    f"[SkillEvo-GEE] Agent: {agent} | stage: {stage} "
                    f"| elapsed: {int(now - started)}s{suffix}",
                    flush=True,
                )
                next_heartbeat = now + max(status_interval_sec, 1.0)
            worker.join(timeout=1.0)

        if "error" in result:
            raise result["error"]  # type: ignore[misc]
        completed = result.get("completed")
        if not isinstance(completed, subprocess.CompletedProcess):
            raise RuntimeError("Hermes process ended without a completion result")
        return completed

    def _new_workflow_states(self, before: set[str]) -> list[Path]:
        paths = [
            path for path in (self.project_root / "runs").glob("req-*/state.json")
            if path.parent.name not in before
        ]
        return sorted(paths, key=lambda path: path.stat().st_mtime)

    @staticmethod
    def _load_state(path: Path) -> dict[str, object] | None:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

    @staticmethod
    def _stage_index(stage: str) -> int:
        order = ["requirement", "capability", "knowledge", "data", "planning", "code", "execution", "audit"]
        try:
            return order.index(stage)
        except ValueError:
            return len(order)

    @staticmethod
    def _read_final_response(stderr: str) -> str | None:
        matches = re.findall(r"session_id:\s*(local-[0-9a-f]+)", stderr)
        if not matches:
            return None
        local_app_data = os.environ.get("LOCALAPPDATA")
        hermes_home = Path(os.environ.get("HERMES_HOME") or (Path(local_app_data) / "hermes" if local_app_data else ""))
        database = hermes_home / "state.db"
        if not database.is_file():
            return None
        try:
            with sqlite3.connect(database) as connection:
                row = connection.execute(
                    "SELECT content FROM messages "
                    "WHERE session_id = ? AND role = 'assistant' "
                    "AND content IS NOT NULL AND content != '' "
                    "ORDER BY id DESC LIMIT 1",
                    (matches[-1],),
                ).fetchone()
        except sqlite3.Error:
            return None
        return str(row[0]) if row else None

    def _write_process_log(self, completed: subprocess.CompletedProcess[str]) -> Path:
        log_dir = self.project_root / "runs" / "hermes-logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        log_path = log_dir / f"{stamp}-{uuid4().hex[:8]}.log"
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
        outcome = "succeeded" if completed.returncode == 0 else "failed"
        failure_summary = ""
        if completed.returncode != 0:
            final_line = next(
                (line.strip() for line in reversed((stderr or stdout).splitlines()) if line.strip()),
                "No stderr/stdout failure detail was returned by Hermes.",
            )
            failure_summary = f"failure_summary: {final_line[:1000]}\n"
        log_path.write_text(
            f"outcome: {outcome}\n"
            f"success: {str(completed.returncode == 0).lower()}\n"
            f"exit_code: {completed.returncode}\n"
            f"finished_at: {datetime.now(timezone.utc).isoformat()}\n"
            f"{failure_summary}"
            "\n--- stdout ---\n"
            f"{stdout}"
            "\n--- stderr ---\n"
            f"{stderr}",
            encoding="utf-8",
        )
        return log_path.relative_to(self.project_root)

