---
id: SUBTASK-PHENOLOGY-THRESHOLD-CLASSIFY-001
kind: subtask
title: EVI 百分位阈值物候阶段分类
version: 0.1.0
status: experimental
summary: 结合 EVI 水平和生长方向，以规则方式标记返青、成熟、衰老和枯黄阶段。
tags: [phenology, percentile, rule-classification]
references: []
source: raw_GEE_case/GEE训练教程_EVI植物生长季节表型分类.md
operation: required
---

# Purpose

使用区域/时序百分位阈值与上升下降状态对物候阶段进行规则分类。

## Operation classification

`required`。该操作是其所属 Task 核心分析链的一部分。

## Procedure

计算低、高 EVI 阈值；上升期按低高区间区分返青和成熟，下降期按高阈值区分衰老与枯黄，输出离散类别波段。

## Constraints

- 阈值需要作物、区域和年份验证，案例值不能直接迁移。
- 多个类别掩膜应互斥，并明确无数据与未分类像元。
- 模态时间序列只能描述主导类别，可能隐藏空间异质性。

## Example

### Scenario

EVI 方向与百分位物候规则

Source: `raw_GEE_case/GEE训练教程_EVI植物生长季节表型分类.md`

### Implementation

```javascript
var stage = ee.Image(0)
  .where(growing.and(evi.gt(lower)).and(evi.lte(upper)), 1)
  .where(growing.and(evi.gt(upper)), 2)
  .where(growing.not().and(evi.gt(upper)), 3)
  .where(growing.not().and(evi.lte(upper)), 4)
  .rename('phenological_stage');
```

### Validation

Status: `required` operation; knowledge status follows frontmatter and requires Task-level execution evidence.

### Limitations

类别 0 需要定义为未分类而非有效阶段；百分位参数须由区域样本或文献校准。
