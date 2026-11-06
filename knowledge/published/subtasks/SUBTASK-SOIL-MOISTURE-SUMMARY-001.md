---
id: SUBTASK-SOIL-MOISTURE-SUMMARY-001
kind: subtask
title: 土壤湿度空间汇总与区域时间序列
version: 0.1.0
status: experimental
summary: 生成土壤湿度时间均值图，并对每期影像执行区域统计形成时间序列。
tags: [soil-moisture, spatial-summary, time-series]
references: []
source: raw_GEE_case/GEE训练教程_TerraClimate土壤湿度分析.md
operation: required
---

# Purpose

从预处理集合生成空间概览与区域统计序列。

## Operation classification

`required`。该操作是其所属 Task 核心分析链的一部分。

## Procedure

用集合时间均值生成地图层；逐期以适配的 reducer 和尺度对研究区归约，保留日期、统计值和有效像元信息。

## Constraints

- 调色板最小/最大值必须来源于数据分布或产品范围。
- 区域均值可能掩盖空间异质性，应同时记录有效面积或分区结果。
- Code Editor 图表和 UI 图例不是无头执行环境的审计输出。

## Example

### Scenario

土壤湿度空间均值与区域序列

Source: `raw_GEE_case/GEE训练教程_TerraClimate土壤湿度分析.md`

### Implementation

```javascript
var meanImage = soil.mean();
var rows = soil.map(function(image) {
  var value = image.reduceRegion({
    reducer: ee.Reducer.mean(), geometry: aoi, scale: scale, maxPixels: 1e9
  }).get('soil');
  return ee.Feature(null, {date: image.date().format('YYYY-MM'), soil: value});
});
```

### Validation

Status: `required` operation; knowledge status follows frontmatter and requires Task-level execution evidence.

### Limitations

地图可视化范围需要从统计量确定；跨多个国家或不连续几何的均值必须解释其空间含义。
