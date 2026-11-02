from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AssetKind(StrEnum):
    CAPABILITY = "capability"
    TASK = "task"
    SUBTASK = "subtask"


class AssetStatus(StrEnum):
    DRAFT = "draft"
    CANDIDATE = "candidate"
    EXPERIMENTAL = "experimental"
    VERIFIED = "verified"
    DEPRECATED = "deprecated"
    MERGED = "merged"


class KnowledgeMetadata(StrictModel):
    id: str = Field(pattern=r"^[A-Z][A-Z0-9-]+$")
    kind: AssetKind
    title: str = Field(min_length=1)
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    status: AssetStatus
    summary: str = Field(min_length=1)
    tags: list[str] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)
    source: str | None = None
    verified_at: datetime | None = None


class KnowledgeAsset(StrictModel):
    metadata: KnowledgeMetadata
    body: str
    path: str


class RequirementSpec(StrictModel):
    request_id: str
    objective: str
    region: str | None = None
    time_range: str | None = None
    data_preferences: list[str] = Field(default_factory=list)
    output_requirements: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    unknowns: list[str] = Field(default_factory=list)


class KnowledgeReference(StrictModel):
    asset_id: str
    version: str
    purpose: str


class AnalysisStep(StrictModel):
    step_id: str
    title: str
    objective: str
    inputs: list[str]
    outputs: list[str]
    knowledge: list[KnowledgeReference]
    acceptance_criteria: list[str]


class AnalysisPlan(StrictModel):
    request_id: str
    objective: str
    assumptions: list[str]
    boundaries: list[str]
    steps: list[AnalysisStep]
    pending_confirmations: list[str] = Field(default_factory=list)


class ExecutionStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    TIMED_OUT = "timed_out"


class WorkflowStage(StrEnum):
    REQUIREMENT = "requirement"
    CAPABILITY = "capability"
    KNOWLEDGE = "knowledge"
    DATA = "data"
    PLANNING = "planning"
    CODE = "code"
    EXECUTION = "execution"
    AUDIT = "audit"
    AWAITING_USER = "awaiting_user"
    COMPLETED = "completed"
    FAILED = "failed"


class FailureClass(StrEnum):
    DATA = "data"
    PLAN = "plan"
    METHOD = "method"
    CODE = "code"
    PERMISSION = "permission"
    USER_INPUT = "user_input"
    UNKNOWN = "unknown"


class WorkflowState(StrictModel):
    request: RequirementSpec
    stage: WorkflowStage = WorkflowStage.REQUIREMENT
    artifact_paths: dict[str, str] = Field(default_factory=dict)
    retry_counts: dict[str, int] = Field(default_factory=dict)
    last_failure_class: FailureClass | None = None
    last_failure: str | None = None
    updated_at: datetime


class GEEExecutionRecord(StrictModel):
    execution_id: str
    status: ExecutionStatus
    script_path: str
    output_path: str
    started_at: datetime
    finished_at: datetime | None = None
    elapsed_ms: int | None = None
    cloud_success_count: int = 0
    cloud_failure_count: int = 0
    report: dict[str, Any] = Field(default_factory=dict)
    stderr: str = ""


class EvolutionOperation(StrEnum):
    ADD = "add"
    MODIFY = "modify"
    MERGE = "merge"


class EvolutionCandidate(StrictModel):
    candidate_id: str
    operation: EvolutionOperation
    source_refs: list[str]
    target_asset_ids: list[str]
    rationale: str
    validation_evidence: list[str] = Field(default_factory=list)
    approved: bool = False

