from __future__ import annotations

from collections import Counter
from pathlib import Path
import re

from knowledge.frontmatter import parse_markdown
from models import KnowledgeAsset


_ALLOWED_REFERENCE_KINDS = {
    "capability": {"task"},
    "task": {"subtask"},
    "subtask": set(),
}

_SUBTASK_HEADINGS = (
    "# Purpose",
    "## Operation classification",
    "## Procedure",
    "## Constraints",
    "## Example",
    "### Scenario",
    "### Implementation",
    "### Validation",
    "### Limitations",
)

_TASK_HEADINGS = (
    "# Goal",
    "## Applicability and boundaries",
    "## Inputs",
    "## Outputs",
    "## Required workflow",
    "## Optional workflow",
    "## Data dependencies",
    "## Acceptance criteria",
    "## User confirmations",
)


def _has_canonical_headings(body: str, headings: tuple[str, ...]) -> bool:
    """Require each canonical Markdown heading exactly once and in order."""
    positions: list[int] = []
    for heading in headings:
        matches = list(re.finditer(rf"(?m)^{re.escape(heading)}\s*$", body))
        if len(matches) != 1:
            return False
        positions.append(matches[0].start())
    return positions == sorted(positions)


def _section(body: str, heading: str, next_heading: str) -> str:
    start = body.find(heading) + len(heading)
    end = body.find(next_heading, start)
    return body[start:end]


def _subtask_ids(markdown: str) -> set[str]:
    return set(re.findall(r"SUBTASK-[A-Z0-9-]+", markdown))


class KnowledgeCatalog:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self._assets: dict[str, KnowledgeAsset] | None = None

    def load(self) -> dict[str, KnowledgeAsset]:
        assets: dict[str, KnowledgeAsset] = {}
        duplicates: list[str] = []
        for path in sorted(self.root.rglob("*.md")):
            asset = parse_markdown(path)
            asset_id = asset.metadata.id
            if asset_id in assets:
                duplicates.append(asset_id)
            assets[asset_id] = asset
        if duplicates:
            raise ValueError(f"Duplicate asset IDs: {', '.join(sorted(set(duplicates)))}")
        self._assets = assets
        return assets

    @property
    def assets(self) -> dict[str, KnowledgeAsset]:
        return self._assets if self._assets is not None else self.load()

    def get(self, asset_id: str) -> KnowledgeAsset:
        try:
            return self.assets[asset_id]
        except KeyError as exc:
            raise KeyError(f"Unknown knowledge asset: {asset_id}") from exc

    def list(self, kind: str | None = None, status: str | None = None) -> list[KnowledgeAsset]:
        values = self.assets.values()
        return sorted(
            (
                asset
                for asset in values
                if (kind is None or asset.metadata.kind.value == kind)
                and (status is None or asset.metadata.status.value == status)
            ),
            key=lambda asset: asset.metadata.id,
        )

    def search(self, query: str, limit: int = 10) -> list[tuple[KnowledgeAsset, int]]:
        terms = [term.lower() for term in query.split() if term.strip()]
        ranked: list[tuple[KnowledgeAsset, int]] = []
        for asset in self.assets.values():
            meta = asset.metadata
            high = f"{meta.id} {meta.title} {meta.summary} {' '.join(meta.tags)}".lower()
            low = asset.body.lower()
            score = sum(high.count(term) * 5 + low.count(term) for term in terms)
            if score:
                ranked.append((asset, score))
        ranked.sort(key=lambda item: (-item[1], item[0].metadata.id))
        return ranked[:limit]

    def validate(self) -> dict[str, object]:
        assets = self.assets
        missing: list[dict[str, str]] = []
        invalid_kinds: list[dict[str, str]] = []
        missing_examples: list[dict[str, str]] = []
        missing_example_code: list[dict[str, str]] = []
        invalid_subtask_structure: list[dict[str, str]] = []
        invalid_task_structure: list[dict[str, str]] = []
        invalid_task_operations: list[dict[str, str]] = []
        invalid_capability_structure: list[dict[str, str]] = []
        for asset in assets.values():
            if asset.metadata.kind.value == "subtask":
                if "## Example" not in asset.body:
                    missing_examples.append({
                        "asset_id": asset.metadata.id,
                        "error": "subtask body must contain an Example section",
                    })
                if "```" not in asset.body:
                    missing_example_code.append({
                        "asset_id": asset.metadata.id,
                        "error": "subtask body must embed Example implementation code",
                    })
                if not _has_canonical_headings(asset.body, _SUBTASK_HEADINGS):
                    invalid_subtask_structure.append({
                        "asset_id": asset.metadata.id,
                        "error": "subtask must contain each required heading exactly once in canonical order",
                    })
            if asset.metadata.kind.value == "task":
                if not _has_canonical_headings(asset.body, _TASK_HEADINGS):
                    invalid_task_structure.append({
                        "asset_id": asset.metadata.id,
                        "error": "task must contain each required heading exactly once in canonical order",
                    })
                else:
                    required_ids = _subtask_ids(_section(
                        asset.body, "## Required workflow", "## Optional workflow"
                    ))
                    optional_ids = _subtask_ids(_section(
                        asset.body, "## Optional workflow", "## Data dependencies"
                    ))
                    declared_ids = set(asset.metadata.references)
                    if required_ids | optional_ids != declared_ids:
                        invalid_task_operations.append({
                            "asset_id": asset.metadata.id,
                            "error": "frontmatter references must equal required and optional workflow references",
                        })
                    for subtask_id, expected in (
                        *((item, "required") for item in required_ids),
                        *((item, "optional") for item in optional_ids),
                    ):
                        target = assets.get(subtask_id)
                        actual = target.metadata.operation.value if target and target.metadata.operation else "missing"
                        if actual != expected:
                            invalid_task_operations.append({
                                "asset_id": asset.metadata.id,
                                "subtask_id": subtask_id,
                                "error": f"{expected} workflow references operation: {actual}",
                            })
            if asset.metadata.kind.value == "capability":
                if "# Published capabilities" not in asset.body or "## Routing rule" not in asset.body:
                    invalid_capability_structure.append({
                        "asset_id": asset.metadata.id,
                        "error": "capability must define Published capabilities and Routing rule",
                    })
            for reference in asset.metadata.references:
                if reference not in assets:
                    missing.append({"asset_id": asset.metadata.id, "missing_reference": reference})
                    continue
                target = assets[reference]
                allowed = _ALLOWED_REFERENCE_KINDS[asset.metadata.kind.value]
                if target.metadata.kind.value not in allowed:
                    invalid_kinds.append({
                        "asset_id": asset.metadata.id,
                        "reference": reference,
                        "expected_kinds": ",".join(sorted(allowed)) or "none",
                        "actual_kind": target.metadata.kind.value,
                    })
        kinds = Counter(asset.metadata.kind.value for asset in assets.values())
        statuses = Counter(asset.metadata.status.value for asset in assets.values())
        return {
            "ok": (
                not missing
                and not invalid_kinds
                and not missing_examples
                and not missing_example_code
                and not invalid_subtask_structure
                and not invalid_task_structure
                and not invalid_task_operations
                and not invalid_capability_structure
            ),
            "asset_count": len(assets),
            "kinds": dict(sorted(kinds.items())),
            "statuses": dict(sorted(statuses.items())),
            "missing_references": missing,
            "invalid_reference_kinds": invalid_kinds,
            "subtasks_without_examples": missing_examples,
            "subtasks_without_example_code": missing_example_code,
            "invalid_subtask_structure": invalid_subtask_structure,
            "invalid_task_structure": invalid_task_structure,
            "invalid_task_operations": invalid_task_operations,
            "invalid_capability_structure": invalid_capability_structure,
        }

