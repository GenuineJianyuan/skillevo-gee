---
name: skillevo-evolution-agent
description: Use only when explicitly adding, modifying, merging, validating, reviewing, or publishing SkillEvo-GEE Task or Subtask knowledge and embedded Examples.
---

# Skill Evolution Agent

Evolution starts only after analysis audit. Read the relevant guide in
`knowledge/evolution/` before acting. The audit recommendation selects Add or
Modify; never override it silently.

## Rules

- source material first enters `knowledge/candidates/`;
- maintain the hierarchy `capabilities -> Task -> Subtask`, with Example code
  and evidence embedded as the terminal section of its owning Subtask;
- Task references only Subtask; Subtask has no child asset layer;
- preserve source, version, status, limitations, and validation evidence;
- use semantic similarity only to propose merge candidates;
- validate structure and references before requesting publication;
- run applicable GEE code and attach evidence;
- show the proposed diff and affected references;
- create candidates with `skillevo_evolution operation=create` only when
  `audit.json` marks them eligible;
- decompose an Add result into complete Task, required/optional Subtasks, and
  embedded Examples, then propose the capability description update;
- for Modify, preserve stable IDs, increment versions, list all affected
  references, and include before/after evidence;
- validate the complete overlaid catalog before requesting approval;
- call approve only after the human user explicitly accepts the solution and
  proposed knowledge diff; publish only after that recorded approval.

Hermes `skills.write_approval=true` protects Hermes Skill files, but domain
publication still requires this candidate/review/publish process.

