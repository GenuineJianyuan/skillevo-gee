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

## Inputs

- An accessible Earth Engine image ID.
- Display bands and visualization range.
- A map center used as the validation-region center.
- Sampling radius and scale.

## Outputs

- Original-image small-region statistics.
- Resampled-image small-region statistics.
- Execution and cloud-request status.

## Workflow

1. Load the fixed image using [`SUBTASK-GEE-IMAGE-LOAD-001`](../subtasks/SUBTASK-GEE-IMAGE-LOAD-001.md).
2. Apply bicubic resampling using [`SUBTASK-IMAGE-RESAMPLE-001`](../subtasks/SUBTASK-IMAGE-RESAMPLE-001.md).
3. Compute bounded regional summaries using [`SUBTASK-REGION-STATS-001`](../subtasks/SUBTASK-REGION-STATS-001.md).
4. Confirm that all expected cloud outputs succeeded and contain valid pixels.

## Boundaries

- Bicubic resampling is intended for continuous-valued imagery, not class labels.
- A successful request validates execution only.
- The current worker supports `ee.Image` layers and a limited Code Editor API subset.

## Acceptance criteria

- Earth Engine authentication and initialization succeed.
- Original and resampled outputs both return successful cloud evaluations.
- Selected bands contain at least one valid pixel in the validation region.

