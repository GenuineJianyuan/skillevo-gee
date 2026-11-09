---
id: TASK-SOIL-SALINITY-VISUALIZATION-001
kind: task
title: Regional Soil-Salinity Mapping with Water Masking
version: 0.2.0
status: experimental
summary: Load the AOI, salinity data, and MOD44W from the source workflow, create a land-only salinity layer, and optionally produce a thematic visualization.
tags: [gee, soil-salinity, water-mask]
references: [SUBTASK-AOI-DEFINE-001, SUBTASK-SALINITY-LAND-MASK-001, SUBTASK-THEMATIC-LEGEND-001, SUBTASK-MAP-PRESENTATION-001]
source: raw_GEE_case MOD44W India soil-salinity visualization tutorial
---

# Goal
Generate a regional soil-salinity raster with water areas excluded.
## Applicability and boundaries
Applies when salinity assets are accessible and the water product encoding is known. Do not assume private assets are available.
## Inputs
AOI, salinity asset, water product and period, salinity units, and optional classification settings.
## Outputs
Land-only salinity layer, with optional map styling and legend.
## Required workflow
1. Load and verify the AOI: [`SUBTASK-AOI-DEFINE-001`](../subtasks/SUBTASK-AOI-DEFINE-001.md).
2. Load salinity data and MOD44W, then construct a land mask: [`SUBTASK-SALINITY-LAND-MASK-001`](../subtasks/SUBTASK-SALINITY-LAND-MASK-001.md).
3. Apply the mask, summarize, and clip salinity: [`SUBTASK-SALINITY-LAND-MASK-001`](../subtasks/SUBTASK-SALINITY-LAND-MASK-001.md).
## Optional workflow
1. Define salinity classes and a legend: [`SUBTASK-THEMATIC-LEGEND-001`](../subtasks/SUBTASK-THEMATIC-LEGEND-001.md).
2. Add map layers: [`SUBTASK-MAP-PRESENTATION-001`](../subtasks/SUBTASK-MAP-PRESENTATION-001.md).
## Data dependencies
Salinity asset, MOD44W, and AOI.
## Acceptance criteria
Assets are accessible, water encoding is correct, the land mask is valid, and salinity units are explicit.
## User confirmations
Provide or confirm private-asset access, class definitions, and visualization requirements.
