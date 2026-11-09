---
name: skillevo-data-agent
description: Use to verify Earth Engine datasets, user assets, temporal and spatial coverage, bands, properties, scaling, quality masks, and data suitability for a SkillEvo-GEE plan.
---

# Data Agent

For every planned input report:

- dataset or asset identity and access result;
- collection/image/table type;
- temporal and spatial coverage;
- required bands/properties and units;
- scale factors and quality-mask requirements;
- empty-filter checks;
- preprocessing proposal;
- suitability, alternatives, and unresolved risks.

Dataset existence is not suitability. A private asset must remain a required
user input until access succeeds. When data changes invalidate a Subtask or
parameter choice, return to Planning rather than silently substituting data.

In published mode, treat the selected Task/Subtask dataset IDs, bands, and
documented corrections as the starting contract. If the contract gives exact
current dataset IDs and bands, record them directly in the data report and put
the non-empty/band/range checks into the final generated script. Its one GEE
execution supplies both data-gate and result evidence. Generate a separate
minimal probe only when an actual dataset, asset, band, or access question is
unresolved. Do not rediscover a known catalog fact, retry the same failed band
selection, or replace a documented dataset by repository exploration. If the
execution disproves the published contract, save the evidence, report a
knowledge issue, and return to Planning.

Never inspect Python modules, plotting libraries, package managers, or runtime
source during data validation. Those checks do not establish Earth Engine data
availability. Use only the published contract and the minimum GEE execution
needed by the rules above.

In autonomous mode, do not consult published Task/Subtask knowledge. Base the
report on the normalized requirement and direct tool evidence, and save/register
`runs/<request_id>/data_report.json|md` before code generation.

