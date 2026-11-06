---
id: SUBTASK-CLIMATE-WATER-BALANCE-001
kind: subtask
title: 月尺度降水与 PET 水量平衡
version: 0.1.0
status: experimental
summary: 将降水和潜在蒸散集合按月份聚合并计算 P-PET 水量平衡。
tags: [chirps, terraclimate, monthly, water-balance]
references: []
source: raw_GEE_case/GEE教程_CHIRPS_TerraClimate_SPEI干旱指数.md
operation: required
---

# Purpose

对齐 CHIRPS 日降水与 TerraClimate PET，按明确年月聚合后计算水量平衡。

## Operation classification

`required`。该操作是其所属 Task 核心分析链的一部分。

## Procedure

分别对每个年月过滤并求和，统一波段名、单位、投影语义和时间属性，再计算 `P - PET`。

## Constraints

- 不应把多个年份的同名月份直接合成一幅图，除非目标确实是多年月份气候态。
- PET 比例因子必须在相减前应用；时间端点采用半开区间更稳妥。
- 两个集合的月份必须一一对应，并检查空集合。

## Example

### Scenario

CHIRPS 与 TerraClimate 月水量平衡

Source: `raw_GEE_case/GEE教程_CHIRPS_TerraClimate_SPEI干旱指数.md`

### Implementation

```javascript
function monthlySum(collection, year, month, outputBand) {
  var start = ee.Date.fromYMD(year, month, 1);
  return collection.filterDate(start, start.advance(1, 'month'))
    .sum().rename(outputBand)
    .set({'year': year, 'month': month, 'system:time_start': start.millis()});
}
var balance = precipitationMonth.subtract(petMonth).rename('water_balance');
```

### Validation

Status: `required` operation; knowledge status follows frontmatter and requires Task-level execution evidence.

### Limitations

原教程按月份跨年份求和，可能丢失逐年月序列；正式实现必须显式遍历 year-month，并核对 PET 比例因子。
