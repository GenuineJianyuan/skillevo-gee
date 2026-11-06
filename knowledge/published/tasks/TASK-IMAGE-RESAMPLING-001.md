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

适用于连续值影像的受控重采样对比，不适用于分类标签。该 Task 只验证指定影像、
投影和小区域统计链是否可执行，不据此判断重采样方法的普遍科学适用性。

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

- 固定且可访问的 Earth Engine 影像资产 ID。
- 明确的连续值波段、原始投影、目标尺度和有效统计区域。
- 当前 worker 对 `ee.Image` 图层和受限 Code Editor API 子集的支持。

## Acceptance criteria

- Earth Engine authentication and initialization succeed.
- Original and resampled outputs both return successful cloud evaluations.
- Selected bands contain at least one valid pixel in the validation region.

## User confirmations

- 确认影像资产、对比波段、验证区域与统计尺度。
- 若目标数据是类别数据，应拒绝 bicubic 路径并重新规划方法。

