---
id: TASK-WIND-SPEED-TIMESERIES-001
kind: task
title: ERA5 风速时间序列与表格导出
version: 0.1.0
status: experimental
summary: 从 ERA5 风矢量分量计算风速，生成区域时间序列并导出日期和值。
tags: [gee, era5, wind-speed, time-series, csv]
references: [SUBTASK-WIND-SPEED-DERIVATION-001, SUBTASK-TIMESERIES-TABLE-EXPORT-001]
source: raw_GEE_case/GEE训练教程_ERA5风速时序与CSV导出.md
---

# 目标

计算给定区域和时段的风速，并形成可视化时间序列与 CSV 表格。

## 工作流

1. 使用 [`SUBTASK-WIND-SPEED-DERIVATION-001`](../subtasks/SUBTASK-WIND-SPEED-DERIVATION-001.md) 从 u/v 分量计算风速影像集合。
2. 使用 [`SUBTASK-TIMESERIES-TABLE-EXPORT-001`](../subtasks/SUBTASK-TIMESERIES-TABLE-EXPORT-001.md) 做区域归约、日期编码和表格导出。

## 输入与输出

- 输入：ROI、ERA5 产品与分量波段、时间范围、归约尺度。
- 输出：风速影像集合、区域时间序列、日期—风速表格。

## 边界与验收

- 必须固定具体 u/v 波段，避免正则选择到不同高度或统计口径的多个波段。
- 多点 FeatureCollection 的区域均值含义必须与研究设计一致。
- 导出前检查空值、时间属性、单位和任务状态。

