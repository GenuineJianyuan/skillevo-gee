from __future__ import annotations

from collections import Counter
from pathlib import Path

from knowledge.frontmatter import parse_markdown
from models import KnowledgeAsset


_ALLOWED_REFERENCE_KINDS = {
    "capability": {"task"},
    "task": {"subtask"},
    "subtask": set(),
}


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
            ),
            "asset_count": len(assets),
            "kinds": dict(sorted(kinds.items())),
            "statuses": dict(sorted(statuses.items())),
            "missing_references": missing,
            "invalid_reference_kinds": invalid_kinds,
            "subtasks_without_examples": missing_examples,
            "subtasks_without_example_code": missing_example_code,
        }

