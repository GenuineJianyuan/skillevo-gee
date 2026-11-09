---
id: TASK-WIND-SPEED-TIMESERIES-001
kind: task
title: ERA5 Wind-Speed Time Series with Optional CSV Export
version: 0.2.0
status: experimental
summary: Define the ROI from the source workflow, load ERA5, calculate wind speed and regional time series, and optionally plot or export the results.
tags: [gee, era5, wind-speed, time-series]
references: [SUBTASK-AOI-DEFINE-001, SUBTASK-COLLECTION-FILTER-001, SUBTASK-WIND-SPEED-DERIVATION-001, SUBTASK-TIMESERIES-TABLE-EXPORT-001, SUBTASK-MAP-PRESENTATION-001, SUBTASK-DRIVE-EXPORT-001]
source: raw_GEE_case ERA5 wind-speed time-series and CSV-export tutorial
---

# Goal
Calculate a wind-speed series for a target region and period, producing auditable date-value records.
## Applicability and boundaries
Applies to ERA5 u/v components with explicit height and temporal-statistic semantics.
## Inputs
ROI, ERA5 product, u/v bands, current or historical period, and reduction scale.
## Outputs
Wind-speed collection, regional time-series table, and optional chart and CSV.
## Required workflow
1. Define the ROI: [`SUBTASK-AOI-DEFINE-001`](../subtasks/SUBTASK-AOI-DEFINE-001.md).
2. Load and filter ERA5: [`SUBTASK-COLLECTION-FILTER-001`](../subtasks/SUBTASK-COLLECTION-FILTER-001.md).
3. Derive wind speed from u/v: [`SUBTASK-WIND-SPEED-DERIVATION-001`](../subtasks/SUBTASK-WIND-SPEED-DERIVATION-001.md).
4. Reduce by region and retain dates: [`SUBTASK-TIMESERIES-TABLE-EXPORT-001`](../subtasks/SUBTASK-TIMESERIES-TABLE-EXPORT-001.md).
## Optional workflow
1. Display a time-series chart: [`SUBTASK-MAP-PRESENTATION-001`](../subtasks/SUBTASK-MAP-PRESENTATION-001.md).
2. Export historical results as CSV: [`SUBTASK-DRIVE-EXPORT-001`](../subtasks/SUBTASK-DRIVE-EXPORT-001.md).
## Data dependencies
Daily ERA5 product and ROI.
## Acceptance criteria
Select exactly one u/v band pair, ensure the collection is non-empty, specify wind-speed units, and validate dates and values in the time-series table.
## User confirmations
Confirm height, product version, period, ROI aggregation semantics, and whether export is required.
