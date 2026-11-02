from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from uuid import uuid4

from models import FailureClass, RequirementSpec, WorkflowStage, WorkflowState


_ALLOWED_TRANSITIONS = {
    WorkflowStage.REQUIREMENT: {WorkflowStage.CAPABILITY, WorkflowStage.AWAITING_USER, WorkflowStage.FAILED},
    WorkflowStage.CAPABILITY: {WorkflowStage.KNOWLEDGE, WorkflowStage.AWAITING_USER, WorkflowStage.FAILED},
    WorkflowStage.KNOWLEDGE: {WorkflowStage.DATA, WorkflowStage.PLANNING, WorkflowStage.FAILED},
    WorkflowStage.DATA: {WorkflowStage.PLANNING, WorkflowStage.AWAITING_USER, WorkflowStage.FAILED},
    WorkflowStage.PLANNING: {WorkflowStage.CODE, WorkflowStage.DATA, WorkflowStage.AWAITING_USER, WorkflowStage.FAILED},
    WorkflowStage.CODE: {WorkflowStage.EXECUTION, WorkflowStage.PLANNING, WorkflowStage.FAILED},
    WorkflowStage.EXECUTION: {WorkflowStage.AUDIT, WorkflowStage.CODE, WorkflowStage.DATA, WorkflowStage.FAILED},
    WorkflowStage.AUDIT: {WorkflowStage.COMPLETED, WorkflowStage.CODE, WorkflowStage.DATA, WorkflowStage.PLANNING, WorkflowStage.AWAITING_USER, WorkflowStage.FAILED},
    WorkflowStage.AWAITING_USER: {WorkflowStage.REQUIREMENT, WorkflowStage.DATA, WorkflowStage.PLANNING, WorkflowStage.FAILED},
    WorkflowStage.COMPLETED: set(),
    WorkflowStage.FAILED: set(),
}


_FAILURE_ROLLBACK = {
    FailureClass.DATA: WorkflowStage.DATA,
    FailureClass.PLAN: WorkflowStage.PLANNING,
    FailureClass.METHOD: WorkflowStage.KNOWLEDGE,
    FailureClass.CODE: WorkflowStage.CODE,
    FailureClass.PERMISSION: WorkflowStage.AWAITING_USER,
    FailureClass.USER_INPUT: WorkflowStage.AWAITING_USER,
    FailureClass.UNKNOWN: WorkflowStage.FAILED,
}


def initialize_requirement(
    objective: str,
    region: str | None = None,
    time_range: str | None = None,
) -> RequirementSpec:
    return RequirementSpec(
        request_id=f"req-{uuid4().hex}",
        objective=objective,
        region=region,
        time_range=time_range,
        unknowns=[
            field
            for field, value in (("region", region), ("time_range", time_range))
            if not value
        ],
    )


class WorkflowStore:
    def __init__(self, runs_dir: Path):
        self.runs_dir = runs_dir

    def initialize(self, requirement: RequirementSpec) -> tuple[WorkflowState, Path]:
        state = WorkflowState(request=requirement, updated_at=datetime.now(timezone.utc))
        return state, self.save(state)

    def path_for(self, request_id: str) -> Path:
        return self.runs_dir / request_id / "state.json"

    def load(self, request_id: str) -> WorkflowState:
        return WorkflowState.model_validate_json(self.path_for(request_id).read_text(encoding="utf-8"))

    def save(self, state: WorkflowState) -> Path:
        target = self.path_for(state.request.request_id)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(state.model_dump_json(indent=2) + "\n", encoding="utf-8")
        return target

    def transition(self, state: WorkflowState, target: WorkflowStage) -> WorkflowState:
        if target not in _ALLOWED_TRANSITIONS[state.stage]:
            raise ValueError(f"Invalid workflow transition: {state.stage.value} -> {target.value}")
        return state.model_copy(update={"stage": target, "updated_at": datetime.now(timezone.utc)})

    def route_failure(
        self,
        state: WorkflowState,
        failure_class: FailureClass,
        message: str,
        max_retries: int = 2,
    ) -> WorkflowState:
        key = failure_class.value
        retries = dict(state.retry_counts)
        retries[key] = retries.get(key, 0) + 1
        target = _FAILURE_ROLLBACK[failure_class]
        if retries[key] > max_retries:
            target = WorkflowStage.FAILED
        return state.model_copy(update={
            "stage": target,
            "retry_counts": retries,
            "last_failure_class": failure_class,
            "last_failure": message,
            "updated_at": datetime.now(timezone.utc),
        })

