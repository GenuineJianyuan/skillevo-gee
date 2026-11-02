---
id: TASK-EVI-PHENOLOGY-001
kind: task
title: 基于 EVI 时序的生长季阶段分类
version: 0.1.0
status: experimental
summary: 通过 EVI 时序滞后比较与百分位阈值识别返青、成熟、衰老和枯黄阶段。
tags: [gee, evi, phenology, temporal-join, classification]
references: [SUBTASK-EVI-LAG-SWITCH-001, SUBTASK-PHENOLOGY-THRESHOLD-CLASSIFY-001]
source: raw_GEE_case/GEE训练教程_EVI植物生长季节表型分类.md
---

# 目标

在指定区域内构建 EVI 时序变化方向，并按阈值规则生成物候阶段分类。

## 工作流

1. 使用 [`SUBTASK-EVI-LAG-SWITCH-001`](../subtasks/SUBTASK-EVI-LAG-SWITCH-001.md) 构造滞后 EVI 和生长方向开关。
2. 使用 [`SUBTASK-PHENOLOGY-THRESHOLD-CLASSIFY-001`](../subtasks/SUBTASK-PHENOLOGY-THRESHOLD-CLASSIFY-001.md) 计算百分位阈值并分类阶段。

## 输入与输出

- 输入：AOI、EVI 产品、时间范围、滞后窗口、百分位阈值。
- 输出：带滞后波段和生长开关的集合、物候阶段分类时序。

## 边界与验收

- 原案例称数据为“平滑 EVI”，但代码未实现平滑，应作为待补步骤而非既成事实。
- 滞后匹配可能为空；EVI 缩放因子、质量掩膜和跨年季节必须显式处理。
- 百分位 20/28 是案例参数，不能无依据迁移到其他作物和区域。

