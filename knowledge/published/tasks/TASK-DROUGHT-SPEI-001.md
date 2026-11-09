---
id: TASK-DROUGHT-SPEI-001
kind: task
title: Drought Indicator Analysis Using Climate Water Balance
version: 0.2.0
status: experimental
summary: Define the region and period from the source workflow, load CHIRPS and TerraClimate, aggregate monthly values, compute water balance, and standardize it.
tags: [gee, drought, chirps, terraclimate]
references: [SUBTASK-AOI-DEFINE-001, SUBTASK-COLLECTION-FILTER-001, SUBTASK-CLIMATE-WATER-BALANCE-001, SUBTASK-WATER-BALANCE-STANDARDIZE-001, SUBTASK-MAP-PRESENTATION-001, SUBTASK-DRIVE-EXPORT-001]
source: raw_GEE_case CHIRPS and TerraClimate drought-index tutorial
---

# Goal
Generate monthly water balance and standardized drought indicators for a specified region and year-month range.
## Applicability and boundaries
Applies to CHIRPS precipitation and TerraClimate PET. The source example uses a z-score, not a statistically rigorous SPEI.
## Inputs
AOI, start and end year-month, target month, PET scale factor, and optional export parameters.
## Outputs
Monthly precipitation, monthly PET, water balance, and standardized indicators; optional map and GeoTIFF.
## Required workflow
1. Define the AOI: [`SUBTASK-AOI-DEFINE-001`](../subtasks/SUBTASK-AOI-DEFINE-001.md).
2. Set the period and load CHIRPS/PET: [`SUBTASK-COLLECTION-FILTER-001`](../subtasks/SUBTASK-COLLECTION-FILTER-001.md).
3. Aggregate by year-month and calculate `P-PET`: [`SUBTASK-CLIMATE-WATER-BALANCE-001`](../subtasks/SUBTASK-CLIMATE-WATER-BALANCE-001.md).
4. Standardize the water-balance series: [`SUBTASK-WATER-BALANCE-STANDARDIZE-001`](../subtasks/SUBTASK-WATER-BALANCE-STANDARDIZE-001.md).
## Optional workflow
1. Filter and display a selected month: [`SUBTASK-MAP-PRESENTATION-001`](../subtasks/SUBTASK-MAP-PRESENTATION-001.md).
2. Export a GeoTIFF: [`SUBTASK-DRIVE-EXPORT-001`](../subtasks/SUBTASK-DRIVE-EXPORT-001.md).
## Data dependencies
CHIRPS DAILY, TerraClimate PET, and AOI data.
## Acceptance criteria
Collections are non-empty, year-month pairs align, PET units are correct, standard deviation is non-zero, and outputs contain valid pixels.
## User confirmations
Confirm the AOI, period, target months, and whether maps or exports are required.
