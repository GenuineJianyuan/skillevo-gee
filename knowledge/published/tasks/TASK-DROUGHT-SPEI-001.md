---
id: TASK-DROUGHT-SPEI-001
kind: task
title: 基于气候水量平衡的干旱指数分析
version: 0.1.0
status: experimental
summary: 使用 CHIRPS 降水与 TerraClimate PET 构建月尺度水量平衡并生成标准化干旱指标。
tags: [gee, drought, chirps, terraclimate, spei]
references: [SUBTASK-CLIMATE-WATER-BALANCE-001, SUBTASK-WATER-BALANCE-STANDARDIZE-001]
source: raw_GEE_case/GEE教程_CHIRPS_TerraClimate_SPEI干旱指数.md
---

# 目标

在给定区域和时间范围内计算月尺度降水与潜在蒸散差值，形成可解释的干旱指标序列。

## 工作流

1. 使用 [`SUBTASK-CLIMATE-WATER-BALANCE-001`](../subtasks/SUBTASK-CLIMATE-WATER-BALANCE-001.md) 对齐降水和 PET，并计算月尺度水量平衡。
2. 使用 [`SUBTASK-WATER-BALANCE-STANDARDIZE-001`](../subtasks/SUBTASK-WATER-BALANCE-STANDARDIZE-001.md) 标准化、筛选和导出结果。

## 输入与输出

- 输入：区域、起止年月、降水产品、PET 产品、输出月份。
- 输出：月尺度水量平衡、标准化干旱指标和可选 GeoTIFF。

## 边界与验收

- 原始示例使用 z-score 简化标准化，不是经过概率分布拟合的严格 SPEI。
- 必须核对 PET 缩放因子、时间聚合方式及两个产品的空间尺度。
- 验收至少包含集合非空、月份对应、标准差非零和输出像元有效性。

