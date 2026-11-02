---
id: TASK-SOIL-MOISTURE-TIMESERIES-001
kind: task
title: TerraClimate 土壤湿度空间与时间分析
version: 0.1.0
status: experimental
summary: 过滤 TerraClimate 土壤湿度数据，进行区域裁剪、单位处理、均值制图和时间序列分析。
tags: [gee, terraclimate, soil-moisture, time-series]
references: [SUBTASK-TERRACLIMATE-SOIL-PREPROCESS-001, SUBTASK-SOIL-MOISTURE-SUMMARY-001]
source: raw_GEE_case/GEE训练教程_TerraClimate土壤湿度分析.md
---

# 目标

获取研究区 TerraClimate 土壤湿度数据并生成空间均值图和区域时间序列。

## 工作流

1. 使用 [`SUBTASK-TERRACLIMATE-SOIL-PREPROCESS-001`](../subtasks/SUBTASK-TERRACLIMATE-SOIL-PREPROCESS-001.md) 过滤、裁剪并处理产品单位。
2. 使用 [`SUBTASK-SOIL-MOISTURE-SUMMARY-001`](../subtasks/SUBTASK-SOIL-MOISTURE-SUMMARY-001.md) 计算空间汇总和时间序列。

## 输入与输出

- 输入：几何或行政区、时间范围、`soil` 波段、缩放因子、归约尺度。
- 输出：土壤湿度影像集合、时间均值图、区域均值时间序列。

## 边界与验收

- 原示例用两个相距很远的点筛选国家，区域语义可能不是预期研究区。
- 缩放因子和单位必须依据当前数据目录核验。
- 原图例最小标签 172、大值标签 162 顺序异常，不能作为可靠分类依据。

