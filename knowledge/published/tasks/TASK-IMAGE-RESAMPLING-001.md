---
id: TASK-IMAGE-RESAMPLING-001
kind: task
title: Compare original and bicubic-resampled GEE imagery
version: 1.0.0
status: verified
summary: Execute a bounded comparison of original and bicubic-resampled Landsat imagery using small-region pixel statistics.
tags: [gee, landsat, resampling, validation]
references: [SUBTASK-GEE-IMAGE-LOAD-001, SUBTASK-IMAGE-RESAMPLE-001, SUBTASK-REGION-STATS-001]
source: reference-demo/script_320013.txt
verified_at: 2026-11-02T11:30:59+08:00
---

# Goal

Compare one Earth Engine image before and after bicubic resampling and obtain
real cloud-computed statistics from a small validation region.

## Applicability and boundaries

Applies to controlled comparisons of resampled continuous imagery, not categorical labels. This Task verifies only that the specified image, projection, and small-region statistics workflow executes; it does not establish general scientific suitability of the resampling method.

## Inputs

- An accessible Earth Engine image ID.
- Display bands and visualization range.
- A map center used as the validation-region center.
- Sampling radius and scale.

## Outputs

- Original-image small-region statistics.
- Resampled-image small-region statistics.
- Execution and cloud-request status.

## Required workflow

1. Load the fixed image using [`SUBTASK-GEE-IMAGE-LOAD-001`](../subtasks/SUBTASK-GEE-IMAGE-LOAD-001.md).
2. Apply bicubic resampling using [`SUBTASK-IMAGE-RESAMPLE-001`](../subtasks/SUBTASK-IMAGE-RESAMPLE-001.md).
3. Compute bounded regional summaries using [`SUBTASK-REGION-STATS-001`](../subtasks/SUBTASK-REGION-STATS-001.md).
4. Confirm that all expected cloud outputs succeeded and contain valid pixels.

## Optional workflow

None. All operations are necessary for this bounded comparison Task.

## Data dependencies

- A fixed, accessible Earth Engine image asset ID.
- Explicit continuous-value bands, source projection, target scale, and valid statistics region.
- Support in the current worker for `ee.Image` layers and the supported subset of the Code Editor API.

## Acceptance criteria

- Earth Engine authentication and initialization succeed.
- Original and resampled outputs both return successful cloud evaluations.
- Selected bands contain at least one valid pixel in the validation region.

## User confirmations

- Confirm the image asset, comparison bands, validation region, and statistics scale.
- If the target data are categorical, reject the bicubic path and replan the method.

