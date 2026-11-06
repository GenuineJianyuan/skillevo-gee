---
id: TASK-DROUGHT-SPEI-001
kind: task
title: 基于气候水量平衡的干旱指标分析
version: 0.2.0
status: experimental
summary: 依据原案例流程定义区域和时段，加载 CHIRPS 与 TerraClimate，聚合月值、计算水量平衡并标准化。
tags: [gee, drought, chirps, terraclimate]
references: [SUBTASK-AOI-DEFINE-001, SUBTASK-COLLECTION-FILTER-001, SUBTASK-CLIMATE-WATER-BALANCE-001, SUBTASK-WATER-BALANCE-STANDARDIZE-001, SUBTASK-MAP-PRESENTATION-001, SUBTASK-DRIVE-EXPORT-001]
source: raw_GEE_case/GEE教程_CHIRPS_TerraClimate_SPEI干旱指数.md
---

# Goal
生成指定区域和年月的月尺度水量平衡与标准化干旱指标。
## Applicability and boundaries
适用于 CHIRPS 降水与 TerraClimate PET 场景；案例标准化是 z-score，不是严格 SPEI。
## Inputs
AOI、起止年月、目标月份、PET 缩放因子、可选导出参数。
## Outputs
月降水、月 PET、水量平衡、标准化指标；可选地图和 GeoTIFF。
## Required workflow
1. 定义 AOI：[`SUBTASK-AOI-DEFINE-001`](../subtasks/SUBTASK-AOI-DEFINE-001.md)。
2. 设置时段并加载 CHIRPS/PET：[`SUBTASK-COLLECTION-FILTER-001`](../subtasks/SUBTASK-COLLECTION-FILTER-001.md)。
3. 按 year-month 计算月度总和并计算 `P-PET`：[`SUBTASK-CLIMATE-WATER-BALANCE-001`](../subtasks/SUBTASK-CLIMATE-WATER-BALANCE-001.md)。
4. 标准化水量平衡：[`SUBTASK-WATER-BALANCE-STANDARDIZE-001`](../subtasks/SUBTASK-WATER-BALANCE-STANDARDIZE-001.md)。
## Optional workflow
1. 过滤并显示指定月份：[`SUBTASK-MAP-PRESENTATION-001`](../subtasks/SUBTASK-MAP-PRESENTATION-001.md)。
2. 导出 GeoTIFF：[`SUBTASK-DRIVE-EXPORT-001`](../subtasks/SUBTASK-DRIVE-EXPORT-001.md)。
## Data dependencies
CHIRPS DAILY、TerraClimate PET、AOI 数据。
## Acceptance criteria
集合非空、年月对应、PET 单位正确、标准差非零、输出含有效像元。
## User confirmations
确认 AOI、时间范围、目标月份、是否需要地图与导出。
