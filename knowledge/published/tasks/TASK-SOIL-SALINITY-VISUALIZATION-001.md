---
id: TASK-SOIL-SALINITY-VISUALIZATION-001
kind: task
title: 土壤盐分陆地区域可视化
version: 0.1.0
status: experimental
summary: 加载土壤盐分数据，使用水体产品掩膜水域，并生成分级专题地图。
tags: [gee, soil-salinity, water-mask, visualization]
references: [SUBTASK-SALINITY-LAND-MASK-001, SUBTASK-THEMATIC-LEGEND-001]
source: raw_GEE_case/GEE教程_MOD44W印度土壤盐分可视化.md
---

# 目标

为指定行政区或研究区生成排除水体后的土壤盐分专题图。

## 工作流

1. 使用 [`SUBTASK-SALINITY-LAND-MASK-001`](../subtasks/SUBTASK-SALINITY-LAND-MASK-001.md) 加载盐分和水体数据并构建陆地掩膜。
2. 使用 [`SUBTASK-THEMATIC-LEGEND-001`](../subtasks/SUBTASK-THEMATIC-LEGEND-001.md) 映射盐分等级并构建图例。

## 输入与输出

- 输入：AOI、盐分资产、盐分等级定义、水体掩膜时间或版本。
- 输出：陆地区域盐分图层、分级样式和图例。

## 边界与验收

- 原示例依赖私有印度行政区资产和社区开放盐分资产，不能假定所有账户可访问。
- `MODIS/006/MOD44W` 的版本和水体编码必须在运行前核验。
- 图例等级必须来自数据说明，不能仅凭调色板推断科学分类。

