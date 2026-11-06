---
id: SUBTASK-EVI-LAG-SWITCH-001
kind: subtask
title: EVI 滞后匹配与生长方向开关
version: 0.1.0
status: experimental
summary: 为 EVI 影像匹配较早观测并依据当前值与滞后值关系构建生长方向波段。
tags: [evi, temporal-join, lag, growing-season]
references: []
source: raw_GEE_case/GEE训练教程_EVI植物生长季节表型分类.md
operation: required
---

# Purpose

为每个时相寻找指定窗口内的前一有效 EVI 观测，并判断植被指数上升或下降。

## Operation classification

`required`。该操作是其所属 Task 核心分析链的一部分。

## Procedure

用 `maxDifference` 与时间先后过滤器执行 temporal join，选择最近的早期影像作为滞后波段，再比较当前和滞后 EVI。

## Constraints

- 必须先应用质量掩膜和比例因子。
- 没有匹配影像时不得直接调用 `first().rename()`。
- 比值在滞后值接近零时不稳定，差值或稳健阈值可能更合适。

## Example

### Scenario

EVI 时间滞后 Join

Source: `raw_GEE_case/GEE训练教程_EVI植物生长季节表型分类.md`

### Implementation

```javascript
var condition = ee.Filter.and(
  ee.Filter.maxDifference({difference: lagMillis,
    leftField: 'system:time_start', rightField: 'system:time_start'}),
  ee.Filter.greaterThan({leftField: 'system:time_start', rightField: 'system:time_start'})
);
var joined = ee.Join.saveBest('previous', 'time_delta').apply(current, current, condition);
```

### Validation

Status: `required` operation; knowledge status follows frontmatter and requires Task-level execution evidence.

### Limitations

使用前应完成质量掩膜和比例因子处理；必须过滤没有 `previous` 匹配的影像。
