---
id: CAPABILITIES-GEE-001
kind: capability
title: SkillEvo-GEE Published Capability Index
version: 1.0.0
status: verified
summary: Published and validated GEE analysis Tasks currently available to the runtime workflow.
tags: [gee, capability-index]
references:
  - TASK-IMAGE-RESAMPLING-001
  - TASK-DROUGHT-SPEI-001
  - TASK-SOIL-SALINITY-VISUALIZATION-001
  - TASK-WIND-SPEED-TIMESERIES-001
  - TASK-EVI-PHENOLOGY-001
  - TASK-WATER-AREA-TIMESERIES-001
  - TASK-SOIL-MOISTURE-TIMESERIES-001
verified_at: 2026-11-02T11:30:59+08:00
---

# Published capabilities

## Image resampling comparison

- **Task:** `TASK-IMAGE-RESAMPLING-001`
- **Capability:** Load one fixed Earth Engine image, compare its original pixels
  with bicubic resampling, and inspect small-region statistics.
- **Typical use:** Infrastructure validation and resampling behavior checks.
- **Boundary:** This Task does not establish that bicubic resampling is suitable
  for categorical rasters, does not export an image, and does not validate a
  general remote-sensing research conclusion.
- **Evidence:** Successfully executed through the bundled GEE demo on 2026-11-02.

## Experimental capabilities from source cases

The following Tasks are structurally published for retrieval but remain
`experimental`. Their source code has not yet passed the current headless GEE
worker and several cases require private assets, UI, Export, or scientific
parameter review.

| Task | Capability | Important boundary |
|---|---|---|
| [`TASK-DROUGHT-SPEI-001`](tasks/TASK-DROUGHT-SPEI-001.md) | CHIRPS/TerraClimate water-balance drought analysis | Source computes a simplified z-score, not strict SPEI |
| [`TASK-SOIL-SALINITY-VISUALIZATION-001`](tasks/TASK-SOIL-SALINITY-VISUALIZATION-001.md) | Land-only salinity thematic mapping | Depends on private/community assets and Code Editor UI |
| [`TASK-WIND-SPEED-TIMESERIES-001`](tasks/TASK-WIND-SPEED-TIMESERIES-001.md) | ERA5 wind-speed series and CSV | Exact component bands and asynchronous Export require verification |
| [`TASK-EVI-PHENOLOGY-001`](tasks/TASK-EVI-PHENOLOGY-001.md) | EVI lag-based phenology classification | No smoothing/QA in source; thresholds are scenario-specific |
| [`TASK-WATER-AREA-TIMESERIES-001`](tasks/TASK-WATER-AREA-TIMESERIES-001.md) | MNDWI/NDWI water area series | Source threshold and mean-vs-sum area logic require correction |
| [`TASK-SOIL-MOISTURE-TIMESERIES-001`](tasks/TASK-SOIL-MOISTURE-TIMESERIES-001.md) | TerraClimate soil-moisture map and series | Scale factor, AOI semantics, and legend values require verification |

