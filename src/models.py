from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


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


class OperationRequirement(StrEnum):
    REQUIRED = "required"
    OPTIONAL = "optional"


class CoverageRoute(StrEnum):
    MATCHED = "matched"
    PARTIAL = "partial"
    UNMATCHED = "unmatched"


class KnowledgeMode(StrEnum):
    PUBLISHED = "published"
    AUTONOMOUS = "autonomous"


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
    operation: OperationRequirement | None = None

    @model_validator(mode="after")
    def validate_operation_scope(self):
        if self.kind == AssetKind.SUBTASK and self.operation is None:
            raise ValueError("subtask metadata requires operation: required|optional")
        if self.kind != AssetKind.SUBTASK and self.operation is not None:
            raise ValueError("operation is only valid for subtask assets")
        return self


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
    PENDING_AUTONOMOUS_PLANNING = "pending_autonomous_planning"
    AUTONOMOUS_PLANNING = "autonomous_planning"
    CANDIDATE_PREPARATION = "candidate_preparation"
    AWAITING_APPROVAL = "awaiting_approval"
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
    routing_reason: str | None = None
    coverage_route: CoverageRoute | None = None
    knowledge_mode: KnowledgeMode | None = None
    candidate_id: str | None = None
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


class CandidateStatus(StrEnum):
    DRAFT = "draft"
    VALIDATED = "validated"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"


class AuditRecommendation(StrEnum):
    ADD = "add"
    MODIFY = "modify"
    REJECT = "reject"
    NEEDS_MORE_EVIDENCE = "needs_more_evidence"


class AuditReport(StrictModel):
    request_id: str
    execution_passed: bool
    data_passed: bool
    plan_passed: bool
    acceptance_passed: bool
    candidate_eligible: bool
    recommendation: AuditRecommendation
    findings: list[str] = Field(default_factory=list)
    scientific_limitations: list[str] = Field(default_factory=list)
    knowledge_issue: str | None = None
    evidence_paths: list[str] = Field(default_factory=list)
    audited_at: datetime

    @model_validator(mode="after")
    def validate_candidate_eligibility(self):
        passes = (
            self.execution_passed
            and self.data_passed
            and self.plan_passed
            and self.acceptance_passed
        )
        recommended = self.recommendation in {
            AuditRecommendation.ADD,
            AuditRecommendation.MODIFY,
        }
        if self.candidate_eligible != (passes and recommended):
            raise ValueError(
                "candidate_eligible requires all audit gates and an add/modify recommendation"
            )
        return self


class EvolutionCandidate(StrictModel):
    candidate_id: str
    request_id: str
    operation: EvolutionOperation
    status: CandidateStatus = CandidateStatus.DRAFT
    audit_recommendation: AuditRecommendation
    source_refs: list[str]
    target_asset_ids: list[str]
    rationale: str
    validation_evidence: list[str] = Field(default_factory=list)
    proposed_files: list[str] = Field(default_factory=list)
    validation_result: dict[str, Any] | None = None
    approved_by: str | None = None
    approved_at: datetime | None = None
    published_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def validate_operation_targets(self):
        if self.operation == EvolutionOperation.MODIFY and not self.target_asset_ids:
            raise ValueError("modify candidate requires at least one target asset ID")
        if self.operation == EvolutionOperation.ADD and self.target_asset_ids:
            raise ValueError("add candidate cannot declare existing target asset IDs")
        if self.audit_recommendation.value != self.operation.value:
            raise ValueError("candidate operation must match the audit recommendation")
        return self

