"""Hermes tools for the workspace-owned SkillEvo-GEE application."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any


def _project_root(ctx) -> Path:
    configured = os.environ.get("SKILLEVO_GEE_ROOT")
    candidates = [Path(configured)] if configured else []
    root_pointer = Path(__file__).resolve().parent / "project-root.txt"
    if root_pointer.is_file():
        pointer_value = root_pointer.read_text(encoding="utf-8-sig").strip()
        if pointer_value:
            candidates.append(Path(pointer_value))
    session_cwd = ctx.session_cwd()
    if session_cwd:
        current = Path(session_cwd).resolve()
        candidates.extend((current, *current.parents))
    for candidate in candidates:
        if (candidate / "pyproject.toml").is_file() and (candidate / "src" / "cli.py").is_file():
            return candidate.resolve()
    raise RuntimeError("Start Hermes in the SkillEvo-GEE workspace or set SKILLEVO_GEE_ROOT")


def _run(ctx, arguments: list[str], timeout: float = 240) -> str:
    root = _project_root(ctx)
    env = os.environ.copy()
    source = str(root / "src")
    env["PYTHONPATH"] = source + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    project_python = os.environ.get("SKILLEVO_GEE_PYTHON") or shutil.which("python")
    if not project_python:
        project_python = sys.executable
    completed = subprocess.run(
        [project_python, "-m", "cli", *arguments],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )
    if completed.stdout.strip():
        return completed.stdout.strip()
    return json.dumps({"ok": False, "exit_code": completed.returncode, "error": completed.stderr[-8000:]})


def register(ctx) -> None:
    def catalog_handler(args: dict, **_: Any) -> str:
        operation = str(args.get("operation", "list"))
        command = ["catalog", operation]
        if args.get("query"):
            command += ["--query", str(args["query"])]
        if args.get("asset_id"):
            command += ["--id", str(args["asset_id"])]
        if args.get("kind"):
            command += ["--kind", str(args["kind"])]
        if args.get("status"):
            command += ["--status", str(args["status"])]
        if args.get("limit") is not None and operation == "search":
            command += ["--limit", str(args["limit"])]
        return _run(ctx, command, timeout=30)

    def workflow_handler(args: dict, **_: Any) -> str:
        operation = str(args.get("operation", "init"))
        if operation == "defer":
            command = [
                "workflow", "defer",
                "--request-id", str(args["request_id"]),
                "--reason", str(args["reason"]),
            ]
        else:
            command = ["workflow", "init", "--objective", str(args["objective"])]
            if args.get("region"):
                command += ["--region", str(args["region"])]
            if args.get("time_range"):
                command += ["--time-range", str(args["time_range"])]
        return _run(ctx, command, timeout=30)

    def gee_handler(args: dict, **_: Any) -> str:
        command = ["gee", "execute", "--script", str(args["script_path"])]
        if args.get("output_path"):
            command += ["--output", str(args["output_path"])]
        for key, flag in (("timeout_sec", "--timeout-sec"), ("sample_radius_m", "--sample-radius-m"), ("sample_scale_m", "--sample-scale-m")):
            if args.get(key) is not None:
                command += [flag, str(args[key])]
        return _run(ctx, command, timeout=float(args.get("timeout_sec", 180)) + 30)

    catalog_schema = {
        "name": "skillevo_catalog",
        "description": "List, search, load, or validate the published SkillEvo-GEE hierarchy.",
        "parameters": {"type": "object", "properties": {
            "operation": {"type": "string", "enum": ["list", "search", "get", "validate"]},
            "query": {"type": "string"}, "asset_id": {"type": "string"},
            "kind": {"type": "string", "enum": ["capability", "task", "subtask"]},
            "status": {"type": "string"},
            "limit": {"type": "integer", "minimum": 1, "maximum": 50}},
            "required": ["operation"]},
    }
    workflow_schema = {
        "name": "skillevo_workflow_init",
        "description": "Initialize a request or defer an uncovered request to autonomous-planning pending.",
        "parameters": {"type": "object", "properties": {
            "operation": {"type": "string", "enum": ["init", "defer"]},
            "objective": {"type": "string"}, "region": {"type": "string"},
            "time_range": {"type": "string"}, "request_id": {"type": "string"},
            "reason": {"type": "string"}}, "required": ["operation"]},
    }
    gee_schema = {
        "name": "skillevo_gee_execute",
        "description": "Run trusted local GEE JavaScript with explicit GEE proxy configuration.",
        "parameters": {"type": "object", "properties": {
            "script_path": {"type": "string"}, "output_path": {"type": "string"},
            "timeout_sec": {"type": "number", "minimum": 1, "maximum": 1800},
            "sample_radius_m": {"type": "number", "minimum": 1},
            "sample_scale_m": {"type": "number", "minimum": 1}},
            "required": ["script_path"]},
    }
    ctx.register_tool(name="skillevo_catalog", toolset="skillevo_gee", handler=catalog_handler,
                      description=catalog_schema["description"], schema=catalog_schema)
    ctx.register_tool(name="skillevo_workflow_init", toolset="skillevo_gee", handler=workflow_handler,
                      description=workflow_schema["description"], schema=workflow_schema)
    ctx.register_tool(name="skillevo_gee_execute", toolset="skillevo_gee", handler=gee_handler,
                      description=gee_schema["description"], schema=gee_schema)

