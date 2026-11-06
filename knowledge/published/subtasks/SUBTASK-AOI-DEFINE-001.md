---
id: SUBTASK-AOI-DEFINE-001
kind: subtask
title: 定义和验证分析区域
version: 0.1.0
status: experimental
summary: 将用户几何、点集或行政区资产转换为语义明确且可用于过滤、裁剪和归约的 AOI。
tags: [aoi, geometry, boundary]
references: []
source: raw_GEE_case
operation: required
---

# Purpose

为后续数据过滤和空间计算建立明确的研究区域。

## Operation classification

`required`。所有当前业务 Task 都依赖空间范围；地图居中和边界显示不是本操作的必要部分。

## Procedure

读取用户几何或可访问的边界资产，检查几何类型、有效性和空间语义；必要时合并或缓冲，并输出单一 AOI geometry。

## Constraints

不得把跨区域多点 `filterBounds` 返回的多个行政区隐式当作目标区域；私有资产必须先验证权限；缓冲距离和投影需明确。

## Example

### Scenario

从 GAUL 国家边界中选择与用户几何相交的区域。

### Implementation

```javascript
var candidates = ee.FeatureCollection('FAO/GAUL/2015/level0')
  .filterBounds(userGeometry);
var aoi = candidates.geometry();
```

### Validation

检查候选数量、AOI 面积、边界范围以及与用户目标的语义一致性。

### Limitations

相交过滤不等于名称级行政区选择；跨国或不连续区域需要用户确认。
