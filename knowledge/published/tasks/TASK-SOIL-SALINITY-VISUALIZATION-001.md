---
id: TASK-SOIL-SALINITY-VISUALIZATION-001
kind: task
title: 土壤盐分陆地区域制图
version: 0.2.0
status: experimental
summary: 依据原案例加载 AOI、盐分和 MOD44W，构建陆地盐分图层并按需生成专题表达。
tags: [gee, soil-salinity, water-mask]
references: [SUBTASK-AOI-DEFINE-001, SUBTASK-SALINITY-LAND-MASK-001, SUBTASK-THEMATIC-LEGEND-001, SUBTASK-MAP-PRESENTATION-001]
source: raw_GEE_case/GEE教程_MOD44W印度土壤盐分可视化.md
---

# Goal
生成排除水体后的区域土壤盐分栅格。
## Applicability and boundaries
适用于可访问的盐分资产和已知编码的水体产品；私有资产不可假定可用。
## Inputs
AOI、盐分资产、水体产品与时间、盐分单位；可选分级配置。
## Outputs
陆地盐分图层；可选地图样式和图例。
## Required workflow
1. 加载并确认 AOI：[`SUBTASK-AOI-DEFINE-001`](../subtasks/SUBTASK-AOI-DEFINE-001.md)。
2. 加载盐分数据、MOD44W 并构建陆地掩膜：[`SUBTASK-SALINITY-LAND-MASK-001`](../subtasks/SUBTASK-SALINITY-LAND-MASK-001.md)。
3. 掩膜、汇总并裁剪盐分：[`SUBTASK-SALINITY-LAND-MASK-001`](../subtasks/SUBTASK-SALINITY-LAND-MASK-001.md)。
## Optional workflow
1. 建立盐分等级和图例：[`SUBTASK-THEMATIC-LEGEND-001`](../subtasks/SUBTASK-THEMATIC-LEGEND-001.md)。
2. 添加地图图层：[`SUBTASK-MAP-PRESENTATION-001`](../subtasks/SUBTASK-MAP-PRESENTATION-001.md)。
## Data dependencies
盐分资产、MOD44W、AOI。
## Acceptance criteria
资产可访问，水体编码正确，陆地掩膜有效，盐分单位明确。
## User confirmations
提供/确认私有资产权限、等级定义和展示需求。
