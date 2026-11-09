---
id: CAPABILITIES-GEE-001
kind: capability
title: SkillEvo-GEE Geospatial Analysis Capability
version: 2.0.0
status: verified
summary: Business-scope taxonomy used to decide whether a normalized GEE request can use the published Task and Subtask knowledge system.
tags: [gee, business-scope, routing]
references: [TASK-DROUGHT-SPEI-001, TASK-WIND-SPEED-TIMESERIES-001, TASK-SOIL-MOISTURE-TIMESERIES-001, TASK-EVI-PHENOLOGY-001, TASK-WATER-AREA-TIMESERIES-001, TASK-SOIL-SALINITY-VISUALIZATION-001, TASK-IMAGE-RESAMPLING-001]
---

# Published capabilities

SkillEvo-GEE transforms user requests into traceable GEE analysis workflows, code, and execution audits using published geospatial-analysis knowledge. The sections below describe the business-analysis capability taxonomy. Tasks are concrete implementation entry points within each capability and are not grouped by verification status or task type.

## Climate and Land-Surface Environmental Time-Series Analysis

Supports data loading, temporal aggregation, indicator calculation, regional statistics, and time-series output for explicit regions, periods, and environmental variables. Current coverage includes precipitation–potential evapotranspiration water balance, ERA5 wind speed, and TerraClimate soil moisture.

- [`TASK-DROUGHT-SPEI-001`](tasks/TASK-DROUGHT-SPEI-001.md): Build monthly water balance and standardized drought indicators from CHIRPS and TerraClimate.
- [`TASK-WIND-SPEED-TIMESERIES-001`](tasks/TASK-WIND-SPEED-TIMESERIES-001.md): Derive wind speed from ERA5 horizontal components and produce regional time series, with optional CSV export.
- [`TASK-SOIL-MOISTURE-TIMESERIES-001`](tasks/TASK-SOIL-MOISTURE-TIMESERIES-001.md): Process TerraClimate soil moisture and produce spatial summaries and regional time series.

## Vegetation Phenology Analysis

Supports preprocessing remote-sensing vegetation-index time series, constructing lag relationships, identifying growth direction, and rule-based phenological-stage classification.

- [`TASK-EVI-PHENOLOGY-001`](tasks/TASK-EVI-PHENOLOGY-001.md): Identify phenological stages using MODIS EVI, lag matching, and percentile thresholds.

## Water Extraction and Surface-Water Change Analysis

Supports optical-remote-sensing water-index calculation, water masking, per-observation pixel-area statistics, and surface-water area time-series analysis.

- [`TASK-WATER-AREA-TIMESERIES-001`](tasks/TASK-WATER-AREA-TIMESERIES-001.md): Estimate surface-water area change using Landsat MNDWI references and MODIS NDWI time series.

## Soil Thematic Mapping

Supports regional clipping, auxiliary masking, and thematic representation of soil-property rasters. Current coverage is limited to combining soil salinity with a water mask.

- [`TASK-SOIL-SALINITY-VISUALIZATION-001`](tasks/TASK-SOIL-SALINITY-VISUALIZATION-001.md): Load salinity data, mask water, and optionally generate a thematic legend.

## Raster Processing and Execution Diagnostics

Supports resampling continuous imagery and computing real-pixel statistics over small regions to verify the GEE execution path and outputs.

- [`TASK-IMAGE-RESAMPLING-001`](tasks/TASK-IMAGE-RESAMPLING-001.md): Compare original and bicubic-resampled imagery and inspect regional statistics.

## Routing rule

The Requirement Agent must first normalize the request, then determine business-scope coverage using only the capability descriptions above:

1. `matched`: At least one capability covers the request's goal, data semantics, and expected outputs. Only then may the agent read Tasks under that capability and continue with knowledge retrieval, data checks, and planning.
2. `partial`: When only part of the goal is covered, identify covered and uncovered parts. Do not combine an existing Task with improvised steps. Record the request in the pending queue, then process the full request in `autonomous` mode without reading published Tasks, Subtasks, or Examples; independently decompose it, inspect data, generate code, execute, and audit.
3. `unmatched`: When no capability matches, do not read published Tasks, Subtasks, or Examples. Add the request to `runs/pending/autonomous-planning/` and enter `autonomous` mode, generating and executing code from the normalized request, direct data evidence, and general GEE/API reasoning.

Autonomous results are first stored in `runs/<request_id>/`. Add/Modify candidates under `knowledge/candidates/` may be created only when execution, plan, and scientific-boundary audits satisfy candidate criteria. Candidates still require explicit user approval, structural validation, and regression checks before publication and before this document is updated.

Matching is based on business semantics, not keyword hits. Asset status and scientific constraints are checked after a Task is selected; they are not grounds for splitting the capability catalog into task-type categories.
