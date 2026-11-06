---
id: TASK-SOIL-MOISTURE-TIMESERIES-001
kind: task
title: TerraClimate 土壤湿度空间与时间分析
version: 0.2.0
status: experimental
summary: 依据原案例定义区域，加载并预处理 TerraClimate soil，生成空间均值和区域时间序列。
tags: [gee, terraclimate, soil-moisture]
references: [SUBTASK-AOI-DEFINE-001, SUBTASK-TERRACLIMATE-SOIL-PREPROCESS-001, SUBTASK-SOIL-MOISTURE-SUMMARY-001, SUBTASK-MAP-PRESENTATION-001]
source: raw_GEE_case/GEE训练教程_TerraClimate土壤湿度分析.md
---

# Goal
获得指定区域土壤湿度空间汇总和时间变化序列。
## Applicability and boundaries
适用于 TerraClimate soil；AOI 语义、缩放因子和单位必须核验。
## Inputs
AOI、时段、soil 波段、缩放因子、归约尺度。
## Outputs
预处理集合、时间均值影像、区域均值时间序列。
## Required workflow
1. 定义研究区并解析行政边界：[`SUBTASK-AOI-DEFINE-001`](../subtasks/SUBTASK-AOI-DEFINE-001.md)。
2. 加载、过滤、缩放、裁剪 soil：[`SUBTASK-TERRACLIMATE-SOIL-PREPROCESS-001`](../subtasks/SUBTASK-TERRACLIMATE-SOIL-PREPROCESS-001.md)。
3. 计算时间均值影像和区域时间序列：[`SUBTASK-SOIL-MOISTURE-SUMMARY-001`](../subtasks/SUBTASK-SOIL-MOISTURE-SUMMARY-001.md)。
## Optional workflow
1. 显示均值图、时序图和图例：[`SUBTASK-MAP-PRESENTATION-001`](../subtasks/SUBTASK-MAP-PRESENTATION-001.md)。
## Data dependencies
TerraClimate、AOI 或 GAUL 边界。
## Acceptance criteria
集合非空，单位正确，区域语义明确，时序值和有效像元存在。
## User confirmations
确认 AOI、单位、尺度和展示需求。
