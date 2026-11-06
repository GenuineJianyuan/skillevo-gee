---
id: TASK-EVI-PHENOLOGY-001
kind: task
title: 基于 EVI 时序的生长季阶段分类
version: 0.2.0
status: experimental
summary: 依据原案例定义 AOI、处理 EVI、构建滞后和生长开关、计算阈值并分类物候阶段。
tags: [gee, evi, phenology]
references: [SUBTASK-AOI-DEFINE-001, SUBTASK-COLLECTION-FILTER-001, SUBTASK-EVI-LAG-SWITCH-001, SUBTASK-PHENOLOGY-THRESHOLD-CLASSIFY-001, SUBTASK-MAP-PRESENTATION-001]
source: raw_GEE_case/GEE训练教程_EVI植物生长季节表型分类.md
---

# Goal
基于 EVI 时序及变化方向识别返青、成熟、衰老和枯黄阶段。
## Applicability and boundaries
适用于有连续 EVI 观测且阈值可校准的区域；原案例未真正实现平滑。
## Inputs
AOI、EVI 产品、时段、质量规则、比例因子、lag days、百分位阈值。
## Outputs
预处理 EVI、滞后波段、生长方向、阈值和物候类别集合。
## Required workflow
1. 定义并缓冲 AOI：[`SUBTASK-AOI-DEFINE-001`](../subtasks/SUBTASK-AOI-DEFINE-001.md)。
2. 加载、过滤、缩放和质量处理 EVI：[`SUBTASK-COLLECTION-FILTER-001`](../subtasks/SUBTASK-COLLECTION-FILTER-001.md)。
3. 创建滞后 EVI 和生长方向：[`SUBTASK-EVI-LAG-SWITCH-001`](../subtasks/SUBTASK-EVI-LAG-SWITCH-001.md)。
4. 计算百分位并分类物候阶段：[`SUBTASK-PHENOLOGY-THRESHOLD-CLASSIFY-001`](../subtasks/SUBTASK-PHENOLOGY-THRESHOLD-CLASSIFY-001.md)。
## Optional workflow
1. 显示类别时间序列：[`SUBTASK-MAP-PRESENTATION-001`](../subtasks/SUBTASK-MAP-PRESENTATION-001.md)。
## Data dependencies
MODIS MYD13Q1 EVI、质量波段、AOI。
## Acceptance criteria
无空 lag 匹配，缩放和 QA 正确，类别互斥，阈值有依据。
## User confirmations
确认作物/地表类型、lag、阈值、是否需要可视化。
