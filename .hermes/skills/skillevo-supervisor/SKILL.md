---
name: skillevo-supervisor
description: Use to coordinate a SkillEvo-GEE request across requirement understanding, capability checking, planning, data checking, code generation, GEE execution, audit, and targeted retry.
---

# SkillEvo-GEE Super Agent

Maintain request state; do not replace specialist judgment with free-form routing.

## Inputs

User request and existing request artifacts under `runs/<request_id>/`.

## Control sequence

1. Invoke the requirement skill when no normalized requirement exists.
2. Let the requirement agent classify the request from `capabilities.md` as
   `matched`, `partial`, or `unmatched` before loading any Task knowledge.
3. Invoke knowledge retrieval and planning only for `matched` requests.
4. Route `partial` and `unmatched` requests to
   `pending_autonomous_planning`; this is a valid deferred outcome, not an
   analysis failure. Do not let them use current Task/Subtask knowledge.
5. Require data findings before approving a plan for code generation.
6. Invoke code generation only for a plan that passes its gate.
7. Send generated code to execution and audit.
8. Route data/empty-collection failures to data checking, workflow or method
   failures to planning, and syntax/API failures to code generation.
9. Stop on missing user assets or retry exhaustion. End deferred requests after
   their pending queue artifact has been persisted.

Never modify published knowledge during a live analysis. Audited lessons may
create an evolution candidate only after the analysis turn is complete.

