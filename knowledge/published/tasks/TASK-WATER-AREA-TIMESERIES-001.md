---
id: TASK-WATER-AREA-TIMESERIES-001
kind: task
title: Multi-Sensor Water Extraction and Surface-Water Area Time Series
version: 0.3.0
status: experimental
summary: Define the ROI, use Landsat MNDWI as a spatial reference, derive MODIS NDWI from official surface-reflectance bands, and calculate surface-water area per observation.
tags: [gee, water, mndwi, ndwi, time-series]
references: [SUBTASK-AOI-DEFINE-001, SUBTASK-COLLECTION-FILTER-001, SUBTASK-MNDWI-WATER-EXTRACTION-001, SUBTASK-WATER-AREA-TIMESERIES-001, SUBTASK-MAP-PRESENTATION-001]
source: raw_GEE_case Landsat 8 and MODIS surface-water time-series tutorial
---

# Goal
Extract water and generate a time series of total surface-water area for the region.
## Applicability and boundaries
Applies to Landsat/MODIS optical indices; thresholds, scale factors, and cloud handling must be verified.
## Inputs
ROI, period, Landsat/MODIS products, QA rules, index thresholds, and reduction scale.
## Outputs
Landsat water reference, MODIS water masks, and a per-observation area series in km2.
## Required workflow
1. Define the ROI: [`SUBTASK-AOI-DEFINE-001`](../subtasks/SUBTASK-AOI-DEFINE-001.md).
2. Load and filter Landsat: [`SUBTASK-COLLECTION-FILTER-001`](../subtasks/SUBTASK-COLLECTION-FILTER-001.md).
3. Calculate Landsat MNDWI: [`SUBTASK-MNDWI-WATER-EXTRACTION-001`](../subtasks/SUBTASK-MNDWI-WATER-EXTRACTION-001.md).
4. Load `MODIS/061/MYD09A1` (or `MODIS/061/MOD09A1`) and derive NDWI as `(sur_refl_b04 - sur_refl_b02) / (sur_refl_b04 + sur_refl_b02)`: [`SUBTASK-COLLECTION-FILTER-001`](../subtasks/SUBTASK-COLLECTION-FILTER-001.md).
5. Apply a threshold, calculate pixel area, and create the observation-area series; aggregate it to calendar months when the user requests monthly output: [`SUBTASK-WATER-AREA-TIMESERIES-001`](../subtasks/SUBTASK-WATER-AREA-TIMESERIES-001.md).
## Optional workflow
1. Display water layers, a chart, and a legend: [`SUBTASK-MAP-PRESENTATION-001`](../subtasks/SUBTASK-MAP-PRESENTATION-001.md).
## Data dependencies
Landsat 8 C02 TOA, official MODIS Collection 6.1 surface reflectance (`MYD09A1` or `MOD09A1`), and an optional administrative boundary. `MOD13A1`/`MOD13Q1` do not provide a direct `NDWI` band or the green `sur_refl_b04` band and must not be selected for this NDWI workflow. The obsolete tutorial collection `MODIS/MYD09GA_006_NDWI` is source evidence only, not the runtime dependency.
## Acceptance criteria
Collections are non-empty; the generated NDWI band is verified; thresholds are justified for the normalized `[-1, 1]` index; area uses `sum`; units are km2; time properties are complete; and requested monthly output contains one explicitly defined statistic per calendar month without silent interpolation.
## User confirmations
Confirm sensors, period, thresholds, cloud handling, and visualization requirements.
