---
id: TASK-WATER-AREA-TIMESERIES-001
kind: task
title: 多源水体提取与水域面积时间序列
version: 0.2.0
status: experimental
summary: 依据原案例定义 ROI，以 Landsat MNDWI 提供空间参考，并以 MODIS NDWI 逐期计算水域面积。
tags: [gee, water, mndwi, ndwi, time-series]
references: [SUBTASK-AOI-DEFINE-001, SUBTASK-COLLECTION-FILTER-001, SUBTASK-MNDWI-WATER-EXTRACTION-001, SUBTASK-WATER-AREA-TIMESERIES-001, SUBTASK-MAP-PRESENTATION-001]
source: raw_GEE_case/GEE训练教程_Landsat8_MODIS水域面积变化时序图表.md
---

# Goal
提取水体并生成区域水域总面积变化序列。
## Applicability and boundaries
适用于 Landsat/MODIS 光学指数；阈值、比例因子和云处理必须验证。
## Inputs
ROI、时段、Landsat/MODIS 产品、QA 规则、指数阈值和统计尺度。
## Outputs
Landsat 水体参考、MODIS 水体掩膜、逐期 km2 面积序列。
## Required workflow
1. 定义 ROI：[`SUBTASK-AOI-DEFINE-001`](../subtasks/SUBTASK-AOI-DEFINE-001.md)。
2. 加载并过滤 Landsat：[`SUBTASK-COLLECTION-FILTER-001`](../subtasks/SUBTASK-COLLECTION-FILTER-001.md)。
3. 计算 Landsat MNDWI：[`SUBTASK-MNDWI-WATER-EXTRACTION-001`](../subtasks/SUBTASK-MNDWI-WATER-EXTRACTION-001.md)。
4. 加载并预处理 MODIS NDWI：[`SUBTASK-COLLECTION-FILTER-001`](../subtasks/SUBTASK-COLLECTION-FILTER-001.md)。
5. 阈值化、计算像元面积并形成日期—面积序列：[`SUBTASK-WATER-AREA-TIMESERIES-001`](../subtasks/SUBTASK-WATER-AREA-TIMESERIES-001.md)。
## Optional workflow
1. 显示水体图层、图表和图例：[`SUBTASK-MAP-PRESENTATION-001`](../subtasks/SUBTASK-MAP-PRESENTATION-001.md)。
## Data dependencies
Landsat 8 C02 TOA、MODIS NDWI、行政边界可选。
## Acceptance criteria
集合非空，阈值有依据，面积使用 sum，单位为 km2，时间属性完整。
## User confirmations
确认传感器、时段、阈值、云处理和展示需求。
