---
id: SUBTASK-WIND-SPEED-DERIVATION-001
kind: subtask
title: 从水平风分量计算风速
version: 0.1.0
status: experimental
summary: 使用 u、v 风分量按 sqrt(u^2+v^2) 计算风速并保留时间属性。
tags: [era5, wind, vector-magnitude]
references: []
source: raw_GEE_case/GEE训练教程_ERA5风速时序与CSV导出.md
operation: required
---

# Purpose

把同一高度和时间统计口径的水平风分量转换为标量风速。

## Operation classification

`required`。该操作是其所属 Task 核心分析链的一部分。

## Procedure

对每幅影像选择一对明确的 u/v 波段，计算 `sqrt(u.pow(2)+v.pow(2))`，重命名为 `wind_speed` 并复制时间属性。

## Constraints

- 不要使用可能匹配多个高度的宽泛正则表达式。
- 两个分量必须具有相同单位、网格和时间统计定义。
- 必须核对 ERA5 数据集 ID 是否仍在目录中可用。

## Example

### Scenario

ERA5 u/v 分量风速计算

Source: `raw_GEE_case/GEE训练教程_ERA5风速时序与CSV导出.md`

### Implementation

```javascript
function addWindSpeed(image) {
  var u = image.select('u_component_of_wind_10m');
  var v = image.select('v_component_of_wind_10m');
  return u.pow(2).add(v.pow(2)).sqrt().rename('wind_speed')
    .copyProperties(image, ['system:time_start']);
}
```

### Validation

Status: `required` operation; knowledge status follows frontmatter and requires Task-level execution evidence.

### Limitations

波段名是语义示例，必须以选定 ERA5 产品的当前目录为准；不得用 `u_.*`、`v_.*` 隐式匹配多组分量。
