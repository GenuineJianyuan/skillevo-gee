---
id: TASK-WIND-SPEED-TIMESERIES-001
kind: task
title: ERA5 风速时间序列与可选 CSV 导出
version: 0.2.0
status: experimental
summary: 依据原案例定义 ROI，加载 ERA5，计算风速、区域时间序列，并按需绘图或导出。
tags: [gee, era5, wind-speed, time-series]
references: [SUBTASK-AOI-DEFINE-001, SUBTASK-COLLECTION-FILTER-001, SUBTASK-WIND-SPEED-DERIVATION-001, SUBTASK-TIMESERIES-TABLE-EXPORT-001, SUBTASK-MAP-PRESENTATION-001, SUBTASK-DRIVE-EXPORT-001]
source: raw_GEE_case/GEE训练教程_ERA5风速时序与CSV导出.md
---

# Goal
计算目标区域指定时期的风速序列，并形成可审计的日期—风速结果。
## Applicability and boundaries
适用于具有明确高度和时间统计口径的 ERA5 u/v 分量。
## Inputs
ROI、ERA5 产品、u/v 波段、当前/历史时段、归约尺度。
## Outputs
风速集合、区域时序表；可选图表和 CSV。
## Required workflow
1. 定义 ROI：[`SUBTASK-AOI-DEFINE-001`](../subtasks/SUBTASK-AOI-DEFINE-001.md)。
2. 加载并过滤 ERA5：[`SUBTASK-COLLECTION-FILTER-001`](../subtasks/SUBTASK-COLLECTION-FILTER-001.md)。
3. 由 u/v 计算风速：[`SUBTASK-WIND-SPEED-DERIVATION-001`](../subtasks/SUBTASK-WIND-SPEED-DERIVATION-001.md)。
4. 区域归约并保留日期：[`SUBTASK-TIMESERIES-TABLE-EXPORT-001`](../subtasks/SUBTASK-TIMESERIES-TABLE-EXPORT-001.md)。
## Optional workflow
1. 显示时间序列图：[`SUBTASK-MAP-PRESENTATION-001`](../subtasks/SUBTASK-MAP-PRESENTATION-001.md)。
2. 导出历史 CSV：[`SUBTASK-DRIVE-EXPORT-001`](../subtasks/SUBTASK-DRIVE-EXPORT-001.md)。
## Data dependencies
ERA5 日尺度产品、ROI。
## Acceptance criteria
固定唯一 u/v 波段，集合非空，风速单位明确，时序表日期和值有效。
## User confirmations
确认高度、产品版本、时间段、ROI 聚合含义和是否导出。
