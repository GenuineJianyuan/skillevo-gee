---
name: skillevo-supervisor
description: Use to coordinate a SkillEvo-GEE request across requirement understanding, capability checking, planning, data checking, code generation, GEE execution, audit, and targeted retry.
---

# SkillEvo-GEE Super Agent

Maintain request state; do not replace specialist judgment with free-form routing.

## Fast deterministic execution contract

- Execute from this Skill and the referenced published Markdown; do not narrate
  chain-of-thought or emit intermediate essays. Persist evidence to `runs/` and
  return only a concise final result.
- Do not explore the repository when a project tool or an exact referenced file
  provides the required information. Do not inspect runtime implementation code
  unless a concrete execution error requires it.
- Before every state-changing tool call, inspect the current state already
  returned by the preceding tool. Invoke `init`, `route`, each transition, and
  each artifact registration exactly once. Never create a second request for the
  same run.
- Follow the legal stage order without speculative transitions:
  `requirement -> capability -> knowledge -> data -> planning -> code -> execution -> audit`.
- For a matched request, treat the selected Task's ordered required workflow as
  authoritative. Do not redesign it or add operations absent from its referenced
  Subtasks. Load the selected Task once, then load all of its referenced Subtasks
  in one `get-many` catalog call. Never load the same asset twice.
- Do not probe Python packages, plotting libraries, repository runtimes, or the
  shell environment. They are not Data-stage evidence. Use the project GEE tool
  and keep unsupported headless chart behavior as an explicit output limitation.
  When the selected published Task/Subtask already specifies exact current
  dataset IDs and bands, do not create a separate probe script: write the data
  report from that contract, put the checks in the final generated script, and
  use its single execution as both data and result evidence. A standalone probe
  is allowed only for an unresolved dataset, asset, band, or access question.
  "No export" means no Earth Engine Export task.
- Perform at most one corrected retry after a failed GEE execution. If that retry
  fails, audit the failure and stop instead of continuing an open-ended repair loop.
- Use parallel read-only retrieval only when inputs are independent. Keep tool
  calls and model turns to the minimum needed to produce the required artifacts.
- Treat matched-request Planning as one bounded assembly operation: use only the
  current request's requirement, knowledge, and data artifacts; write/register
  one concise plan; transition immediately to Code. Never inspect historical
  runs or ask Planning Agent to rediscover or improve the published method.

## Inputs

User request and existing request artifacts under `runs/<request_id>/`.

## Control sequence

1. Invoke the requirement skill when no normalized requirement exists.
2. Let the requirement agent classify the request from `capabilities.md` as
   `matched`, `partial`, or `unmatched` before loading any Task knowledge.
3. For `matched`, set `knowledge_mode=published`, then retrieve only the selected
   Task and its referenced Subtasks.
4. For `partial` or `unmatched`, set `knowledge_mode=autonomous`, persist the
   pending record, immediately start autonomous planning, and continue the run.
   Do not load, cite, adapt, or imitate current Task/Subtask/Example knowledge.
5. In autonomous mode, require a decomposed requirement, explicit assumptions,
   data findings, acceptance criteria, and a saved autonomous plan before code.
6. Require data findings before approving any plan for code generation.
7. Invoke code generation only for a plan that passes its gate.
8. Send generated code to execution and audit.
9. Route data/empty-collection failures to data checking, workflow or method
   failures to planning, and syntax/API failures to code generation.
10. After audit, create an Add or Modify candidate only when the audit marks it
    candidate-eligible. Otherwise complete, reject, or request more evidence.
11. Never approve or publish a candidate without the human user's explicit
    approval. Stop on missing user assets or retry exhaustion.

Never modify published knowledge during live analysis. Autonomous results stay
under `runs/` until audit creates a separate candidate under
`knowledge/candidates/`.

