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
2. Invoke planning only after capability coverage is known.
3. Require data findings before approving a plan for code generation.
4. Invoke code generation only for a plan that passes its gate.
5. Send generated code to execution and audit.
6. Route data/empty-collection failures to data checking, workflow or method
   failures to planning, and syntax/API failures to code generation.
7. Stop on missing user assets, retry exhaustion, or uncovered capability.

Never modify published knowledge during a live analysis. Audited lessons may
create an evolution candidate only after the analysis turn is complete.

