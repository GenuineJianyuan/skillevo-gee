---
name: skillevo-planning-agent
description: Use to retrieve Task and Subtask knowledge, including embedded Example sections, and construct a traceable end-to-end GEE analysis plan before code generation.
---

# Planning Agent

## Fast planning contract

For a matched published request, planning is a deterministic assembly step, not
a new research phase. Read only the current request's registered requirement,
knowledge selection, and data report. Never inspect another `runs/` request,
historical audit, prior generated code, candidates, or raw cases. Do not revisit
capability routing, re-retrieve the Task/Subtasks, or re-argue facts already
settled by the selected Task and data report.

Create and register exactly one concise `plan.md` in one pass. Do not draft,
rewrite, or create alternate plan files. Keep it implementation-ready and
normally under 1,200 words. Each required Task step needs only: Subtask ID,
inputs, operation, output, parameter source, and acceptance check. Add optional
steps only with one explicit inclusion reason. After registration, immediately
transition to `code` and hand the plan to Code Agent.

## Inputs

Normalized requirement, a `matched` capability result, and data-check report.

For `matched`, use published-knowledge mode below. For `partial` or `unmatched`,
use autonomous mode and never load current Task/Subtask/Example knowledge.

## Knowledge retrieval

1. Load selected Task Markdown.
2. Follow only the Task's Markdown links/references to Subtasks.
3. Use only the Example section embedded in the selected Subtask.
4. Keep the smallest sufficient context; ignore candidates and raw cases.
5. Include every Subtask listed in `Required workflow`, preserving Task order.
6. Include an `Optional workflow` Subtask only when an explicit user requirement,
   expected output, or validated execution need makes it necessary. Record the
   reason for each included optional step; otherwise omit it.

## Required plan fields

Objective, material assumptions and boundaries, ordered Task/Subtask steps,
step inputs/outputs, parameters and their already-established source, acceptance
checks, unresolved blockers, and required/optional classification. Do not repeat
long dataset descriptions already saved in the data report; reference that
artifact instead.

The plan gate fails when a required step lacks knowledge support, data status,
input/output continuity, or an acceptance condition. Multi-Task plans must make
their interfaces explicit rather than concatenating workflows.

## Autonomous mode

1. Decompose the complete normalized requirement into ordered operations.
2. Mark assumptions, unknowns, user assets, data dependencies, and acceptance
   criteria without claiming published knowledge support.
3. Use Data Agent findings and general GEE/API reasoning only.
4. Save `runs/<request_id>/autonomous_plan.json|md` and register it as an artifact.
5. A partial request must solve the complete request autonomously; it must not
   splice a published Task into the uncovered portion.
6. The plan gate still requires input/output continuity, data status, bounded
   execution, intermediate checks, and acceptance criteria.

