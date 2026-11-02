from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from models import KnowledgeAsset, KnowledgeMetadata


class FrontmatterError(ValueError):
    pass


def _scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        return [_scalar(part) for part in inner.split(",")] if inner else []
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    if value.lower() in {"null", "none", "~"}:
        return None
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    return value


def _parse_flat_frontmatter(text: str, path: Path) -> dict[str, Any]:
    """Parse the deliberately flat metadata contract used by knowledge assets."""
    result: dict[str, Any] = {}
    current_list: str | None = None
    for line_number, raw_line in enumerate(text.splitlines(), start=2):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if raw_line.startswith("  - ") and current_list:
            result[current_list].append(_scalar(raw_line[4:]))
            continue
        match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*):(?:\s*(.*))?", raw_line)
        if not match:
            raise FrontmatterError(f"Unsupported frontmatter at {path}:{line_number}: {raw_line}")
        key, value = match.group(1), (match.group(2) or "")
        if not value:
            result[key] = []
            current_list = key
        else:
            result[key] = _scalar(value)
            current_list = None
    return result


def parse_markdown(path: Path) -> KnowledgeAsset:
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise FrontmatterError(f"Missing YAML frontmatter: {path}")
    try:
        end = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration as exc:
        raise FrontmatterError(f"Unclosed YAML frontmatter: {path}") from exc

    raw = _parse_flat_frontmatter("\n".join(lines[1:end]), path)
    metadata = KnowledgeMetadata.model_validate(raw)
    body = "\n".join(lines[end + 1 :]).strip()
    if not body:
        raise FrontmatterError(f"Markdown body is empty: {path}")
    return KnowledgeAsset(metadata=metadata, body=body, path=str(path.resolve()))

