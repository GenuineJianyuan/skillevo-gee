from __future__ import annotations

import os
from pathlib import Path


def find_project_root(start: Path | None = None) -> Path:
    configured = os.environ.get("SKILLEVO_GEE_ROOT")
    if configured:
        root = Path(configured).expanduser().resolve()
        if (root / "pyproject.toml").is_file():
            return root
        raise FileNotFoundError(f"SKILLEVO_GEE_ROOT is not a project root: {root}")

    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / "pyproject.toml").is_file() and (candidate / "knowledge").is_dir():
            return candidate
    raise FileNotFoundError("Cannot find SkillEvo-GEE project root")

