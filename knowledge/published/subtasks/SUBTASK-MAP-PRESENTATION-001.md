---
id: SUBTASK-MAP-PRESENTATION-001
kind: subtask
title: GEE 地图、图表与图例展示
version: 0.1.0
status: experimental
summary: 在核心分析结果完成后，按需添加 Code Editor 地图图层、时序图或图例。
tags: [visualization, chart, legend, ui]
references: []
source: raw_GEE_case
operation: optional
---

# Purpose

为人工查看提供展示层，不改变核心分析结果。

## Operation classification

`optional`。只有用户要求可视化或交互展示时才加入计划；无头执行和数值结果不依赖本操作。

## Procedure

根据已验证的输出范围设置可视化参数，添加 Map layer、`ui.Chart` 或与同一分类配置一致的 legend。

## Constraints

`ui.*` 不受当前 headless worker 支持；图例和调色板不得替代单位、阈值和科学分类依据；展示失败不能改变分析结论。

## Example

### Scenario

显示区域时序图。

### Implementation

```javascript
print(ui.Chart.image.series({
  imageCollection: collection,
  region: aoi,
  reducer: ee.Reducer.mean(),
  scale: scale,
  xProperty: 'system:time_start'
}));
```

### Validation

检查展示所用数据与核心输出一致、坐标轴单位明确、无空值误插值。

### Limitations

Code Editor UI 不能作为自动化审计证据。
