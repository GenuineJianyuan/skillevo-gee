---
id: CAPABILITIES-GEE-001
kind: capability
title: SkillEvo-GEE Geospatial Analysis Capability
version: 2.0.0
status: verified
summary: Business-scope taxonomy used to decide whether a normalized GEE request can use the published Task and Subtask knowledge system.
tags: [gee, business-scope, routing]
references: [TASK-DROUGHT-SPEI-001, TASK-WIND-SPEED-TIMESERIES-001, TASK-SOIL-MOISTURE-TIMESERIES-001, TASK-EVI-PHENOLOGY-001, TASK-WATER-AREA-TIMESERIES-001, TASK-SOIL-SALINITY-VISUALIZATION-001, TASK-IMAGE-RESAMPLING-001]
---

# Published capabilities

SkillEvo-GEE 的总能力是：依据已发布的地理空间分析知识，将用户需求转换为可追踪的 GEE 分析流程、代码和执行审计结果。下面按照业务分析体系描述能力范围；Task 是能力分类下的具体实现入口，不按验证状态或任务类型分区。

## 气候与陆面环境时序分析

面向具有明确区域、时间范围和环境变量的数据加载、时间聚合、指标计算、区域统计与时序输出。当前覆盖降水—潜在蒸散水量平衡、ERA5 风速和 TerraClimate 土壤湿度。

- [`TASK-DROUGHT-SPEI-001`](tasks/TASK-DROUGHT-SPEI-001.md)：以 CHIRPS 和 TerraClimate 构建月尺度水量平衡及标准化干旱指标。
- [`TASK-WIND-SPEED-TIMESERIES-001`](tasks/TASK-WIND-SPEED-TIMESERIES-001.md)：由 ERA5 水平风分量计算风速并生成区域时序，按需导出 CSV。
- [`TASK-SOIL-MOISTURE-TIMESERIES-001`](tasks/TASK-SOIL-MOISTURE-TIMESERIES-001.md)：处理 TerraClimate 土壤湿度并生成空间汇总和区域时序。

## 植被物候分析

面向遥感植被指数时序的预处理、滞后关系构建、生长方向判断和规则化物候阶段识别。

- [`TASK-EVI-PHENOLOGY-001`](tasks/TASK-EVI-PHENOLOGY-001.md)：使用 MODIS EVI、滞后匹配和百分位阈值识别物候阶段。

## 水体提取与水域变化分析

面向光学遥感水体指数计算、水体掩膜、逐期像元面积统计和水域面积时序分析。

- [`TASK-WATER-AREA-TIMESERIES-001`](tasks/TASK-WATER-AREA-TIMESERIES-001.md)：结合 Landsat MNDWI 参考与 MODIS NDWI 时序估计水域面积变化。

## 土壤专题制图

面向土壤属性栅格的区域裁剪、辅助掩膜和专题表达。当前仅覆盖土壤盐分与水体掩膜组合场景。

- [`TASK-SOIL-SALINITY-VISUALIZATION-001`](tasks/TASK-SOIL-SALINITY-VISUALIZATION-001.md)：加载盐分数据，排除水体并按需生成专题图例。

## 栅格处理与执行诊断

面向连续型影像的重采样处理和小区域真实像元统计，用于验证 GEE 执行链及处理结果。

- [`TASK-IMAGE-RESAMPLING-001`](tasks/TASK-IMAGE-RESAMPLING-001.md)：比较原始影像与双三次重采样影像并检查区域统计。

## Routing rule

Requirement Agent 必须先将需求规范化，再仅依据上述能力介绍判断业务范围：

1. `matched`：至少一项能力在目标、数据语义和预期输出上可覆盖需求，才允许读取该能力下的 Task，并继续知识检索、数据检查和规划。
2. `partial`：只有部分目标在范围内时，列出已覆盖与未覆盖部分；不得使用现有 Task 补造未覆盖步骤，默认进入待行区，除非用户明确缩小目标。
3. `unmatched`：没有能力匹配时，不读取 Task/Subtask，不依赖当前知识体系生成代码；调用 workflow defer，将请求写入 `runs/pending/autonomous-planning/`。自主规划器尚未实现，当前只入队并报告原因。

匹配依据是业务语义，不是关键词命中。资产状态和科学限制在选中 Task 后再检查，不用于把能力目录拆成不同任务类型。
