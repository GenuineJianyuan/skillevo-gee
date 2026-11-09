# Skill Evolution Policy

Skill evolution changes only the published knowledge context. It does not change the Hermes runtime, Agent roles, orchestration rules, model parameters, or audit standards.

All changes follow this lifecycle:

```text
Source evidence
  → autonomous or published-knowledge run
  → audit
  → candidate assets
  → structure and reference validation
  → applicable GEE validation
  → explicit user approval
  → publication
```

Published-knowledge analyses read only from `knowledge/published/`. The autonomous path does not read published Task/Subtask knowledge; it first stores all evidence under `runs/`.

The design supports `add`, `modify`, and `merge`. The current CLI implements Add/Modify candidate workflows; Merge remains a manually reviewed future operation. Do not update the published `capabilities.md` with candidate Task references before approval and publication.
