---
id: TASK-WATER-AREA-TIMESERIES-001
kind: task
title: 多源水体提取与水域面积时间序列
version: 0.1.0
status: experimental
summary: 使用 Landsat MNDWI 和 MODIS NDWI 提取水体并分析区域水域面积变化。
tags: [gee, water, mndwi, ndwi, landsat, modis, time-series]
references: [SUBTASK-MNDWI-WATER-EXTRACTION-001, SUBTASK-WATER-AREA-TIMESERIES-001]
source: raw_GEE_case/GEE训练教程_Landsat8_MODIS水域面积变化时序图表.md
---

# 目标

基于光学指数识别水体，并生成研究区水域面积随时间变化的序列。

## 工作流

1. 使用 [`SUBTASK-MNDWI-WATER-EXTRACTION-001`](../subtasks/SUBTASK-MNDWI-WATER-EXTRACTION-001.md) 构建 Landsat MNDWI 水体参考图。
2. 使用 [`SUBTASK-WATER-AREA-TIMESERIES-001`](../subtasks/SUBTASK-WATER-AREA-TIMESERIES-001.md) 对 MODIS NDWI 阈值化、计算像元面积并进行时序归约。

## 输入与输出

- 输入：ROI、时段、Landsat/MODIS 产品、云掩膜策略、指数阈值。
- 输出：水体掩膜、面积影像集合、平方公里时间序列。

## 边界与验收

- 原代码把多年 Landsat 集合取中值，仅适合作为空间参考，不代表时间变化。
- 原 MODIS 阈值 `NDWI >= 1` 和面积影像使用 `mean` 归约均需核验；面积通常应使用 `sum`。
- 必须验证产品 ID、比例因子、云/阴影处理和输出单位。

