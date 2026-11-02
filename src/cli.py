from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from gee import GEEExecutor
from hermes_runner import HermesRunner
from knowledge import KnowledgeCatalog
from paths import find_project_root
from workflow import WorkflowStore, initialize_requirement


def _print(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))


def _asset_summary(asset) -> dict[str, Any]:
    metadata = asset.metadata
    return {
        "id": metadata.id,
        "kind": metadata.kind.value,
        "title": metadata.title,
        "version": metadata.version,
        "status": metadata.status.value,
        "summary": metadata.summary,
        "references": metadata.references,
        "path": asset.path,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skillevo-gee")
    commands = parser.add_subparsers(dest="command", required=True)

    run = commands.add_parser("run", help="Run one complete request through Hermes")
    run.add_argument("request", help="Natural-language geospatial analysis request")
    run.add_argument("--reasoning", default="none")
    run.add_argument("--timeout-sec", type=float, default=900)

    catalog = commands.add_parser("catalog")
    catalog_commands = catalog.add_subparsers(dest="catalog_command", required=True)
    listing = catalog_commands.add_parser("list")
    listing.add_argument("--kind")
    listing.add_argument("--status")
    search = catalog_commands.add_parser("search")
    search.add_argument("--query", required=True)
    search.add_argument("--limit", type=int, default=10)
    get = catalog_commands.add_parser("get")
    get.add_argument("--id", required=True)
    catalog_commands.add_parser("validate")

    gee = commands.add_parser("gee")
    gee_commands = gee.add_subparsers(dest="gee_command", required=True)
    execute = gee_commands.add_parser("execute")
    execute.add_argument("--script", type=Path, required=True)
    execute.add_argument("--output", type=Path)
    execute.add_argument("--timeout-sec", type=float, default=180)
    execute.add_argument("--sample-radius-m", type=float, default=300)
    execute.add_argument("--sample-scale-m", type=float, default=30)

    workflow = commands.add_parser("workflow")
    workflow_commands = workflow.add_subparsers(dest="workflow_command", required=True)
    init = workflow_commands.add_parser("init")
    init.add_argument("--objective", required=True)
    init.add_argument("--region")
    init.add_argument("--time-range")
    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    root = find_project_root()

    if args.command == "run":
        return HermesRunner(root).run(args.request, args.reasoning, args.timeout_sec)

    if args.command == "catalog":
        catalog = KnowledgeCatalog(root / "knowledge" / "published")
        if args.catalog_command == "validate":
            result = catalog.validate()
            _print(result)
            return 0 if result["ok"] else 1
        if args.catalog_command == "list":
            _print([_asset_summary(a) for a in catalog.list(args.kind, args.status)])
            return 0
        if args.catalog_command == "get":
            asset = catalog.get(args.id)
            _print({**_asset_summary(asset), "body": asset.body})
            return 0
        if args.catalog_command == "search":
            _print([{**_asset_summary(a), "score": score} for a, score in catalog.search(args.query, args.limit)])
            return 0

    if args.command == "gee" and args.gee_command == "execute":
        record = GEEExecutor(root).execute(
            args.script,
            args.output,
            args.timeout_sec,
            args.sample_radius_m,
            args.sample_scale_m,
        )
        _print(record.model_dump(mode="json"))
        return 0 if record.status.value == "succeeded" else 1

    if args.command == "workflow" and args.workflow_command == "init":
        requirement = initialize_requirement(args.objective, args.region, args.time_range)
        state, path = WorkflowStore(root / "runs").initialize(requirement)
        _print({"state": state.model_dump(mode="json"), "path": str(path)})
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

