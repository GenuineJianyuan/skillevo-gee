---
name: skillevo-evolution-agent
description: Use only when explicitly adding, modifying, merging, validating, reviewing, or publishing SkillEvo-GEE Task or Subtask knowledge and embedded Examples.
---

# Skill Evolution Agent

Evolution operates outside live analysis. Read the relevant guide in
`knowledge/evolution/` before acting.

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
- publish only after explicit approval.

Hermes `skills.write_approval=true` protects Hermes Skill files, but domain
publication still requires this candidate/review/publish process.

