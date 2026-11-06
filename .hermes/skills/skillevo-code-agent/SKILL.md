---
name: skillevo-code-agent
description: Use to generate auditable Google Earth Engine JavaScript from an approved SkillEvo-GEE analysis plan and the Examples embedded in referenced Subtasks.
---

# Code Generation Agent

Generate code from the approved plan, not directly from the user request.

Requirements:

- map each plan step to visible code sections;
- preserve the plan's required-step order and generate optional sections only
  when the approved plan contains them with an inclusion reason;
- use only checked dataset IDs, bands, scale factors, and parameters;
- preserve unknown inputs as named placeholders;
- add checks for collection size, bands, and key intermediate values;
- keep output summaries machine-auditable;
- list plan-step-to-code mappings and remaining placeholders.

Example code is implementation evidence, not authority over the Task plan.
Correct known source defects documented in the Subtask rather than copying them.
Do not claim Code Editor `ui` or `Export` support in the headless worker unless
the execution capability has been extended and tested.

