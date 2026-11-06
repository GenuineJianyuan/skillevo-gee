# SkillEvo-GEE

SkillEvo-GEE is a Hermes-based research system for representing, retrieving,
executing, auditing, and evolving Google Earth Engine analysis knowledge.

Environment prerequisites, exact verified versions, Hermes/plugin setup, GEE
credentials and proxy boundaries, and reproducibility risks are documented in
[`ENVIRONMENT_AND_DEPENDENCIES.md`](ENVIRONMENT_AND_DEPENDENCIES.md).

## Knowledge model

The project deliberately separates Hermes procedural skills from domain assets:

| Layer | Purpose | Location |
|---|---|---|
| Hermes supervisor skill | Enforces the end-to-end control sequence | `.hermes/skills/skillevo-supervisor/` |
| Hermes requirement skill | Normalizes and persists requests | `.hermes/skills/skillevo-requirement-agent/` |
| Hermes planning skill | Resolves Task and Subtask knowledge into a plan | `.hermes/skills/skillevo-planning-agent/` |
| Hermes data skill | Checks datasets, bands, scale, region, and time coverage | `.hermes/skills/skillevo-data-agent/` |
| Hermes code skill | Generates auditable GEE JavaScript from an approved plan | `.hermes/skills/skillevo-code-agent/` |
| Hermes audit skill | Reviews execution evidence and scientific limitations | `.hermes/skills/skillevo-audit-agent/` |
| Hermes evolution skill | Prepares reviewed candidate knowledge changes | `.hermes/skills/skillevo-evolution-agent/` |
| Business capability router | Classifies normalized requests before Task knowledge is loaded | `knowledge/published/capabilities.md` |
| Task | Defines a complete analysis objective and ordered workflow | `knowledge/published/tasks/` |
| Subtask | Defines one reusable algorithmic step and its soft constraints | `knowledge/published/subtasks/` |
| Example section | Scenario-specific code and evidence embedded in its owning Subtask | `knowledge/published/subtasks/*.md` |

Task documents reference Subtask Markdown files. Example is content inside the
owning Subtask rather than a separately indexed asset, and is not divided further.
Every Task separates `Required workflow` from `Optional workflow`; every Subtask
declares `operation: required|optional`. Catalog validation enforces the two
classifications, canonical document structures, and cross-layer references.

The Requirement Agent reads only `capabilities.md` for its first decision.
`matched` requests may continue into Task/Subtask retrieval. `partial` and
`unmatched` requests are stored under `runs/pending/autonomous-planning/` and
must not use the current knowledge hierarchy. This is currently a pending queue,
not an implemented autonomous planner.

Task and Subtask documents are not individual Hermes `SKILL.md` files.
They are versioned domain assets with stable IDs and explicit references. The
Python catalog validates and retrieves them; Hermes loads only the small
procedural skill needed for the current operation.

## Quick start

One-time local setup for the headless GEE tool:

```powershell
Copy-Item config/gee.example.json config/gee.local.json
# Edit project, external credential path, and GEE proxy in gee.local.json.
cd src/gee/runtime
npm ci --omit=dev
cd ../..
```

```powershell
cd "D:\Project\Paper_Projects\GEE Agent\skillevo-gee"
python skillevo.py run "分析 2020-2022 年指定区域的季节性水域面积变化"

# Lower-level diagnostics
python skillevo.py catalog validate
python skillevo.py catalog list
python skillevo.py catalog search --query "Landsat resampling"
python skillevo.py gee execute --script runs/<request_id>/generated.js
```

After `pip install -e .`, the equivalent single command is:

```powershell
skillevo-gee run "分析 2020-2022 年指定区域的季节性水域面积变化"
```

The `run` command is the intended user entry point. Python launches Hermes in
one-shot CLI mode with the Super Agent skill preloaded; Hermes then calls the
project plugin tools and specialist skills. Lower-level commands remain for
testing and maintenance.

The GEE adapter is implemented as the `skillevo_gee_execute` Hermes tool. Its
runtime lives in `src/gee/runtime/` and is configured by the ignored local file
`config/gee.local.json` (copy `config/gee.example.json` to start). The adapter
clears inherited proxy variables and passes the configured proxy explicitly to
the Node worker. Hermes therefore remains on a direct connection while Earth
Engine uses its own proxy. Credentials remain outside the project and are only
referenced by path from the local config.

## Safety boundaries

- Published knowledge is read by the analysis workflow; evolution writes first
  go to `knowledge/candidates/`.
- Hermes is configured with `skills.write_approval: true`; its own Skill writes
  require approval.
- A successful Earth Engine request proves execution, not scientific validity.
- `raw_GEE_case/` is source material, not published knowledge.
- Service-account credentials and local proxy configuration are ignored by Git.

