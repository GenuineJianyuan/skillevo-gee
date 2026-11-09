---
id: TASK-EVI-PHENOLOGY-001
kind: task
title: Growing-Season Stage Classification from EVI Time Series
version: 0.2.0
status: experimental
summary: Define the AOI from the source workflow, process EVI, construct lag and growth-direction signals, calculate thresholds, and classify phenological stages.
tags: [gee, evi, phenology]
references: [SUBTASK-AOI-DEFINE-001, SUBTASK-COLLECTION-FILTER-001, SUBTASK-EVI-LAG-SWITCH-001, SUBTASK-PHENOLOGY-THRESHOLD-CLASSIFY-001, SUBTASK-MAP-PRESENTATION-001]
source: raw_GEE_case EVI phenological-stage classification tutorial
---

# Goal
Identify green-up, maturity, senescence, and dormancy stages from EVI time series and change direction.
## Applicability and boundaries
Applies where continuous EVI observations are available and thresholds can be calibrated. The source example does not implement actual smoothing.
## Inputs
AOI, EVI product, period, quality rules, scale factor, lag days, and percentile thresholds.
## Outputs
Preprocessed EVI, lag bands, growth direction, thresholds, and a phenological-class collection.
## Required workflow
1. Define and buffer the AOI: [`SUBTASK-AOI-DEFINE-001`](../subtasks/SUBTASK-AOI-DEFINE-001.md).
2. Load, filter, scale, and quality-screen EVI: [`SUBTASK-COLLECTION-FILTER-001`](../subtasks/SUBTASK-COLLECTION-FILTER-001.md).
3. Create lagged EVI and growth direction: [`SUBTASK-EVI-LAG-SWITCH-001`](../subtasks/SUBTASK-EVI-LAG-SWITCH-001.md).
4. Calculate percentiles and classify phenological stages: [`SUBTASK-PHENOLOGY-THRESHOLD-CLASSIFY-001`](../subtasks/SUBTASK-PHENOLOGY-THRESHOLD-CLASSIFY-001.md).
## Optional workflow
1. Display the class time series: [`SUBTASK-MAP-PRESENTATION-001`](../subtasks/SUBTASK-MAP-PRESENTATION-001.md).
## Data dependencies
MODIS MYD13Q1 EVI, quality bands, and AOI.
## Acceptance criteria
No lag matches are missing, scaling and QA are correct, classes are mutually exclusive, and thresholds are justified.
## User confirmations
Confirm crop/land-cover type, lag, thresholds, and whether visualization is required.
