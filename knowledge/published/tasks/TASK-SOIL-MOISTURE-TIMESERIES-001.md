---
id: TASK-SOIL-MOISTURE-TIMESERIES-001
kind: task
title: TerraClimate Soil-Moisture Spatial and Temporal Analysis
version: 0.2.0
status: experimental
summary: Define the region from the source workflow, load and preprocess TerraClimate soil, and produce spatial means and regional time series.
tags: [gee, terraclimate, soil-moisture]
references: [SUBTASK-AOI-DEFINE-001, SUBTASK-TERRACLIMATE-SOIL-PREPROCESS-001, SUBTASK-SOIL-MOISTURE-SUMMARY-001, SUBTASK-MAP-PRESENTATION-001]
source: raw_GEE_case TerraClimate soil-moisture analysis tutorial
---

# Goal
Produce spatial summaries and temporal series of soil moisture for the specified region.
## Applicability and boundaries
Applies to TerraClimate soil; AOI semantics, scale factor, and units must be verified.
## Inputs
AOI, period, soil band, scale factor, and reduction scale.
## Outputs
Preprocessed collection, temporal-mean image, and regional-mean time series.
## Required workflow
1. Define the study area and resolve administrative boundaries: [`SUBTASK-AOI-DEFINE-001`](../subtasks/SUBTASK-AOI-DEFINE-001.md).
2. Load, filter, scale, and clip soil: [`SUBTASK-TERRACLIMATE-SOIL-PREPROCESS-001`](../subtasks/SUBTASK-TERRACLIMATE-SOIL-PREPROCESS-001.md).
3. Calculate the temporal-mean image and regional time series: [`SUBTASK-SOIL-MOISTURE-SUMMARY-001`](../subtasks/SUBTASK-SOIL-MOISTURE-SUMMARY-001.md).
## Optional workflow
1. Display the mean map, time-series chart, and legend: [`SUBTASK-MAP-PRESENTATION-001`](../subtasks/SUBTASK-MAP-PRESENTATION-001.md).
## Data dependencies
TerraClimate and an AOI or GAUL boundary.
## Acceptance criteria
The collection is non-empty, units are correct, region semantics are explicit, and the time series and valid pixels are present.
## User confirmations
Confirm the AOI, units, scale, and visualization requirements.
