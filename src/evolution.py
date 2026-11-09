from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import tempfile
from uuid import uuid4

from knowledge import KnowledgeCatalog
from knowledge.frontmatter import parse_markdown
from models import (
    AuditReport,
    AuditRecommendation,
    CandidateStatus,
    EvolutionCandidate,
    EvolutionOperation,
)


_DESTINATIONS = {
    "capabilities.md": Path("capabilities.md"),
    "tasks": Path("tasks"),
    "subtasks": Path("subtasks"),
}


class CandidateStore:
    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        self.candidates_dir = self.project_root / "knowledge" / "candidates"
        self.published_dir = self.project_root / "knowledge" / "published"

    def directory(self, candidate_id: str) -> Path:
        if not candidate_id.startswith("cand-") or not candidate_id.replace("-", "").isalnum():
            raise ValueError(f"Invalid candidate ID: {candidate_id}")
        return self.candidates_dir / candidate_id

    def manifest_path(self, candidate_id: str) -> Path:
        return self.directory(candidate_id) / "candidate.json"

    def create(
        self,
        request_id: str,
        operation: EvolutionOperation,
        recommendation: AuditRecommendation,
        rationale: str,
        source_refs: list[str],
        target_asset_ids: list[str],
        evidence: list[str],
    ) -> tuple[EvolutionCandidate, Path]:
        if recommendation in {AuditRecommendation.REJECT, AuditRecommendation.NEEDS_MORE_EVIDENCE}:
            raise ValueError("Only add or modify audit recommendations can create a candidate")
        request_dir = self.project_root / "runs" / request_id
        if not request_dir.is_dir():
            raise FileNotFoundError(f"Request run directory does not exist: {request_dir}")
        audit_path = request_dir / "audit.json"
        if not audit_path.is_file():
            raise FileNotFoundError("Candidate creation requires runs/<request_id>/audit.json")
        audit = AuditReport.model_validate_json(audit_path.read_text(encoding="utf-8"))
        if audit.request_id != request_id or not audit.candidate_eligible:
            raise ValueError("Audit does not mark this request as candidate eligible")
        if audit.recommendation != recommendation:
            raise ValueError("Candidate recommendation must match audit.json")
        evidence = list(dict.fromkeys([*evidence, *audit.evidence_paths, str(audit_path.relative_to(self.project_root))]))
        now = datetime.now(timezone.utc)
        candidate = EvolutionCandidate(
            candidate_id=f"cand-{uuid4().hex}",
            request_id=request_id,
            operation=operation,
            audit_recommendation=recommendation,
            source_refs=source_refs,
            target_asset_ids=target_asset_ids,
            rationale=rationale,
            validation_evidence=evidence,
            created_at=now,
            updated_at=now,
        )
        directory = self.directory(candidate.candidate_id)
        (directory / "proposed" / "tasks").mkdir(parents=True)
        (directory / "proposed" / "subtasks").mkdir(parents=True)
        self._save(candidate)
        readme = directory / "README.md"
        readme.write_text(
            "# Evolution candidate\n\n"
            f"- Request: `{request_id}`\n"
            f"- Operation: `{operation.value}`\n"
            f"- Status: `{candidate.status.value}`\n\n"
            "Place proposed Task/Subtask Markdown under `proposed/`. Add a proposed "
            "`capabilities.md` only after the Task proposal is complete.\n",
            encoding="utf-8",
        )
        return candidate, directory

    def load(self, candidate_id: str) -> EvolutionCandidate:
        return EvolutionCandidate.model_validate_json(
            self.manifest_path(candidate_id).read_text(encoding="utf-8")
        )

    def list(self) -> list[EvolutionCandidate]:
        manifests = sorted(self.candidates_dir.glob("cand-*/candidate.json"))
        return [EvolutionCandidate.model_validate_json(path.read_text(encoding="utf-8")) for path in manifests]

    def _proposed_files(self, candidate_id: str) -> list[Path]:
        proposed = self.directory(candidate_id) / "proposed"
        files: list[Path] = []
        capability = proposed / "capabilities.md"
        if capability.is_file():
            files.append(capability)
        files.extend(sorted((proposed / "tasks").glob("*.md")))
        files.extend(sorted((proposed / "subtasks").glob("*.md")))
        return files

    def _relative_destination(self, path: Path) -> Path:
        proposed = path.parents[1] if path.parent.name in {"tasks", "subtasks"} else path.parent
        relative = path.relative_to(proposed)
        if relative == Path("capabilities.md"):
            return _DESTINATIONS["capabilities.md"]
        if relative.parts[0] not in {"tasks", "subtasks"}:
            raise ValueError(f"Unsupported proposed path: {relative}")
        return relative

    def validate(self, candidate_id: str) -> EvolutionCandidate:
        candidate = self.load(candidate_id)
        files = self._proposed_files(candidate_id)
        if not files:
            raise ValueError("Candidate has no proposed knowledge files")
        if candidate.operation == EvolutionOperation.ADD:
            if not any(path.parent.name == "tasks" for path in files):
                raise ValueError("Add candidate must contain at least one proposed Task")
            if not any(path.parent.name == "subtasks" for path in files):
                raise ValueError("Add candidate must contain at least one proposed Subtask")
            if not any(path.name == "capabilities.md" for path in files):
                raise ValueError("Add candidate must contain a proposed capabilities.md")

        proposed_asset_ids = {
            parse_markdown(path).metadata.id
            for path in files
            if path.name != "capabilities.md"
        }
        if candidate.operation == EvolutionOperation.MODIFY:
            declared = set(candidate.target_asset_ids)
            if proposed_asset_ids != declared:
                raise ValueError(
                    "Modify proposal asset IDs must exactly equal declared target IDs; "
                    f"proposed={sorted(proposed_asset_ids)}, declared={sorted(declared)}"
                )

        with tempfile.TemporaryDirectory() as directory:
            staged = Path(directory) / "published"
            shutil.copytree(self.published_dir, staged)
            for source in files:
                destination = staged / self._relative_destination(source)
                destination.parent.mkdir(parents=True, exist_ok=True)
                if candidate.operation == EvolutionOperation.ADD and destination.exists() and destination.name != "capabilities.md":
                    raise FileExistsError(f"Add candidate cannot replace published asset: {destination.name}")
                if candidate.operation == EvolutionOperation.MODIFY and not destination.exists() and destination.name != "capabilities.md":
                    raise FileNotFoundError(f"Modify candidate target is not published: {destination.name}")
                shutil.copy2(source, destination)
            result = KnowledgeCatalog(staged).validate()
        if not result["ok"]:
            raise ValueError(f"Candidate catalog validation failed: {json.dumps(result, ensure_ascii=False)}")

        updated = candidate.model_copy(update={
            "status": CandidateStatus.AWAITING_APPROVAL,
            "proposed_files": [str(path.relative_to(self.directory(candidate_id))) for path in files],
            "validation_result": result,
            "updated_at": datetime.now(timezone.utc),
        })
        self._save(updated)
        return updated

    def approve(self, candidate_id: str, approved_by: str) -> EvolutionCandidate:
        candidate = self.load(candidate_id)
        if candidate.status != CandidateStatus.AWAITING_APPROVAL:
            raise ValueError("Candidate must validate successfully before approval")
        now = datetime.now(timezone.utc)
        approved = candidate.model_copy(update={
            "status": CandidateStatus.APPROVED,
            "approved_by": approved_by,
            "approved_at": now,
            "updated_at": now,
        })
        self._save(approved)
        return approved

    def reject(self, candidate_id: str) -> EvolutionCandidate:
        candidate = self.load(candidate_id)
        rejected = candidate.model_copy(update={
            "status": CandidateStatus.REJECTED,
            "updated_at": datetime.now(timezone.utc),
        })
        self._save(rejected)
        return rejected

    def publish(self, candidate_id: str) -> EvolutionCandidate:
        candidate = self.load(candidate_id)
        if candidate.status != CandidateStatus.APPROVED or not candidate.approved_at:
            raise PermissionError("Candidate publication requires explicit recorded approval")
        validated = self.validate(candidate_id)
        approved = validated.model_copy(update={
            "status": CandidateStatus.APPROVED,
            "approved_by": candidate.approved_by,
            "approved_at": candidate.approved_at,
        })
        self._save(approved)

        before = self.directory(candidate_id) / "before"
        files = self._proposed_files(candidate_id)
        applied: list[tuple[Path, Path | None]] = []
        try:
            for source in files:
                relative = self._relative_destination(source)
                destination = self.published_dir / relative
                backup = before / relative if destination.exists() else None
                if backup:
                    backup.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(destination, backup)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
                applied.append((destination, backup))
            final_result = KnowledgeCatalog(self.published_dir).validate()
            if not final_result["ok"]:
                raise ValueError("Published catalog failed validation after applying candidate")
        except Exception:
            for destination, backup in reversed(applied):
                if backup and backup.exists():
                    shutil.copy2(backup, destination)
                elif destination.exists():
                    destination.unlink()
            raise

        now = datetime.now(timezone.utc)
        published = approved.model_copy(update={
            "status": CandidateStatus.PUBLISHED,
            "validation_result": final_result,
            "published_at": now,
            "updated_at": now,
        })
        self._save(published)
        return published

    def _save(self, candidate: EvolutionCandidate) -> Path:
        target = self.manifest_path(candidate.candidate_id)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(candidate.model_dump_json(indent=2) + "\n", encoding="utf-8")
        return target
