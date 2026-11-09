from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any
from datetime import datetime, timezone

from evolution import CandidateStore
from gee import GEEExecutor
from hermes_runner import (
    DEFAULT_MAX_TURNS,
    DEFAULT_PROVIDER,
    DEFAULT_RUN_BUDGET_SEC,
    HermesRunner,
    agent_for_stage,
)
from knowledge import KnowledgeCatalog
from paths import find_project_root
from models import (
    AuditRecommendation,
    AuditReport,
    CoverageRoute,
    EvolutionOperation,
    WorkflowStage,
)
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
    run.add_argument("--provider", default=DEFAULT_PROVIDER)
    run.add_argument("--max-turns", type=int, default=DEFAULT_MAX_TURNS)
    run.add_argument("--run-budget-sec", type=float, default=DEFAULT_RUN_BUDGET_SEC)
    run.add_argument(
        "--status-interval-sec",
        type=float,
        default=15.0,
        help="Seconds between concise Agent/stage heartbeat messages",
    )
    run.add_argument(
        "--show-progress",
        action="store_true",
        help="Show Hermes reasoning/tool previews instead of final output only",
    )

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
    get_many = catalog_commands.add_parser("get-many")
    get_many.add_argument("--id", action="append", required=True)
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
    defer = workflow_commands.add_parser("defer")
    defer.add_argument("--request-id", required=True)
    defer.add_argument("--reason", required=True)
    route = workflow_commands.add_parser("route")
    route.add_argument("--request-id", required=True)
    route.add_argument("--route", choices=[item.value for item in CoverageRoute], required=True)
    route.add_argument("--reason", required=True)
    start_autonomous = workflow_commands.add_parser("start-autonomous")
    start_autonomous.add_argument("--request-id", required=True)
    transition = workflow_commands.add_parser("transition")
    transition.add_argument("--request-id", required=True)
    transition.add_argument("--stage", choices=[item.value for item in WorkflowStage], required=True)
    artifact = workflow_commands.add_parser("artifact")
    artifact.add_argument("--request-id", required=True)
    artifact.add_argument("--name", required=True)
    artifact.add_argument("--path", required=True)
    status = workflow_commands.add_parser("status")
    status_target = status.add_mutually_exclusive_group(required=True)
    status_target.add_argument("--request-id")
    status_target.add_argument("--latest", action="store_true")

    audit = commands.add_parser("audit")
    audit_commands = audit.add_subparsers(dest="audit_command", required=True)
    record = audit_commands.add_parser("record")
    record.add_argument("--request-id", required=True)
    for flag in ("execution-passed", "data-passed", "plan-passed", "acceptance-passed", "candidate-eligible"):
        record.add_argument(f"--{flag}", action=argparse.BooleanOptionalAction, required=True)
    record.add_argument("--recommendation", choices=[item.value for item in AuditRecommendation], required=True)
    record.add_argument("--finding", action="append", default=[])
    record.add_argument("--limitation", action="append", default=[])
    record.add_argument("--knowledge-issue")
    record.add_argument("--evidence", action="append", default=[])

    evolution = commands.add_parser("evolution")
    evolution_commands = evolution.add_subparsers(dest="evolution_command", required=True)
    create = evolution_commands.add_parser("create")
    create.add_argument("--request-id", required=True)
    create.add_argument("--operation", choices=["add", "modify"], required=True)
    create.add_argument("--rationale", required=True)
    create.add_argument("--source-ref", action="append", default=[])
    create.add_argument("--target-id", action="append", default=[])
    create.add_argument("--evidence", action="append", default=[])
    evolution_commands.add_parser("list")
    show = evolution_commands.add_parser("show")
    show.add_argument("--candidate-id", required=True)
    validate = evolution_commands.add_parser("validate")
    validate.add_argument("--candidate-id", required=True)
    approve = evolution_commands.add_parser("approve")
    approve.add_argument("--candidate-id", required=True)
    approve.add_argument("--approved-by", required=True)
    reject = evolution_commands.add_parser("reject")
    reject.add_argument("--candidate-id", required=True)
    publish = evolution_commands.add_parser("publish")
    publish.add_argument("--candidate-id", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    root = find_project_root()

    if args.command == "run":
        return HermesRunner(root).run(
            args.request,
            args.reasoning,
            args.timeout_sec,
            args.provider,
            args.max_turns,
            args.run_budget_sec,
            quiet=not args.show_progress,
            status_interval_sec=args.status_interval_sec,
        )

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
        if args.catalog_command == "get-many":
            _print([
                {**_asset_summary(asset), "body": asset.body}
                for asset in (catalog.get(asset_id) for asset_id in args.id)
            ])
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
    if args.command == "workflow" and args.workflow_command == "defer":
        store = WorkflowStore(root / "runs")
        state = store.load(args.request_id)
        if state.stage == WorkflowStage.REQUIREMENT:
            state = store.transition(state, WorkflowStage.CAPABILITY)
            store.save(state)
        state, path = store.defer_to_autonomous_planning(state, args.reason)
        _print({"state": state.model_dump(mode="json"), "pending_path": str(path)})
        return 0
    if args.command == "workflow" and args.workflow_command == "status":
        store = WorkflowStore(root / "runs")
        if args.latest:
            paths = list((root / "runs").glob("req-*/state.json"))
            if not paths:
                print("No workflow state exists.", file=sys.stderr)
                return 1
            state_path = max(paths, key=lambda path: path.stat().st_mtime)
            request_id = state_path.parent.name
        else:
            request_id = args.request_id
        state = store.load(request_id)
        _print({
            "request_id": state.request.request_id,
            "agent": agent_for_stage(state.stage.value),
            "stage": state.stage.value,
            "coverage_route": state.coverage_route,
            "knowledge_mode": state.knowledge_mode,
            "artifacts": state.artifact_paths,
            "retry_counts": state.retry_counts,
            "last_failure_class": state.last_failure_class,
            "last_failure": state.last_failure,
            "updated_at": state.updated_at,
        })
        return 0
    if args.command == "workflow":
        store = WorkflowStore(root / "runs")
        state = store.load(args.request_id)
        if args.workflow_command == "route":
            state = store.set_capability_route(state, CoverageRoute(args.route), args.reason)
        elif args.workflow_command == "start-autonomous":
            state = store.start_autonomous_planning(state)
        elif args.workflow_command == "transition":
            state = store.save_and_return(store.transition(state, WorkflowStage(args.stage)))
        elif args.workflow_command == "artifact":
            artifact_path = (root / args.path).resolve() if not Path(args.path).is_absolute() else Path(args.path).resolve()
            try:
                artifact_path.relative_to(root)
            except ValueError as exc:
                raise ValueError("Registered artifacts must stay inside the project") from exc
            if not artifact_path.exists():
                raise FileNotFoundError(f"Artifact does not exist: {artifact_path}")
            state = store.register_artifact(state, args.name, str(artifact_path.relative_to(root)))
        _print({"state": state.model_dump(mode="json"), "path": str(store.path_for(args.request_id))})
        return 0

    if args.command == "audit" and args.audit_command == "record":
        report = AuditReport(
            request_id=args.request_id,
            execution_passed=args.execution_passed,
            data_passed=args.data_passed,
            plan_passed=args.plan_passed,
            acceptance_passed=args.acceptance_passed,
            candidate_eligible=args.candidate_eligible,
            recommendation=AuditRecommendation(args.recommendation),
            findings=args.finding,
            scientific_limitations=args.limitation,
            knowledge_issue=args.knowledge_issue,
            evidence_paths=args.evidence,
            audited_at=datetime.now(timezone.utc),
        )
        target = root / "runs" / args.request_id / "audit.json"
        if not target.parent.is_dir():
            raise FileNotFoundError(f"Unknown request run directory: {target.parent}")
        target.write_text(report.model_dump_json(indent=2) + "\n", encoding="utf-8")
        store = WorkflowStore(root / "runs")
        state = store.load(args.request_id)
        if state.stage != WorkflowStage.AUDIT:
            state = store.transition(state, WorkflowStage.AUDIT)
        state = store.register_artifact(state, "audit", str(target.relative_to(root)))
        _print({"audit": report.model_dump(mode="json"), "state": state.model_dump(mode="json"), "path": str(target)})
        return 0

    if args.command == "evolution":
        store = CandidateStore(root)
        if args.evolution_command == "list":
            _print([item.model_dump(mode="json") for item in store.list()])
            return 0
        if args.evolution_command == "show":
            _print(store.load(args.candidate_id).model_dump(mode="json"))
            return 0
        if args.evolution_command == "create":
            recommendation = AuditRecommendation(args.operation)
            candidate, directory = store.create(
                args.request_id,
                EvolutionOperation(args.operation),
                recommendation,
                args.rationale,
                args.source_ref,
                args.target_id,
                args.evidence,
            )
            workflow = WorkflowStore(root / "runs")
            state = workflow.load(args.request_id)
            if state.stage == WorkflowStage.AUDIT:
                state = workflow.save_and_return(workflow.transition(state, WorkflowStage.CANDIDATE_PREPARATION))
            state = state.model_copy(update={"candidate_id": candidate.candidate_id})
            workflow.save(state)
            _print({"candidate": candidate.model_dump(mode="json"), "directory": str(directory)})
            return 0
        if args.evolution_command == "validate":
            candidate = store.validate(args.candidate_id)
        elif args.evolution_command == "approve":
            candidate = store.approve(args.candidate_id, args.approved_by)
        elif args.evolution_command == "reject":
            candidate = store.reject(args.candidate_id)
        elif args.evolution_command == "publish":
            candidate = store.publish(args.candidate_id)
        workflow = WorkflowStore(root / "runs")
        state_path = workflow.path_for(candidate.request_id)
        if state_path.is_file():
            state = workflow.load(candidate.request_id)
            if args.evolution_command == "validate" and state.stage == WorkflowStage.CANDIDATE_PREPARATION:
                workflow.save(workflow.transition(state, WorkflowStage.AWAITING_APPROVAL))
            elif args.evolution_command == "reject" and state.stage == WorkflowStage.AWAITING_APPROVAL:
                workflow.save(workflow.transition(state, WorkflowStage.FAILED))
            elif args.evolution_command == "publish" and state.stage == WorkflowStage.AWAITING_APPROVAL:
                workflow.save(workflow.transition(state, WorkflowStage.COMPLETED))
        _print(candidate.model_dump(mode="json"))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

