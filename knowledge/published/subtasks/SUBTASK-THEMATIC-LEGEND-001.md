---
id: SUBTASK-THEMATIC-LEGEND-001
kind: subtask
title: GEE 专题图分级与图例
version: 0.1.0
status: experimental
summary: 根据已验证的等级阈值和颜色构建专题图层与 Code Editor 图例。
tags: [visualization, legend, ui]
references: []
source: raw_GEE_case/GEE教程_MOD44W印度土壤盐分可视化.md
operation: optional
---

# Purpose

把科学上已定义的分级映射为颜色并在 GEE Code Editor 中显示图例。

## Operation classification

`optional`。该操作只影响展示或交付，不改变核心分析结果。

## Procedure

维护有序的阈值、标签和颜色三元组；地图样式和图例由同一配置生成，避免二者漂移。

## Constraints

- `ui.*` 仅适用于 Code Editor，当前无 UI 的执行 worker 不支持。
- 类别数、阈值数和颜色数必须一致。
- 图例不能替代数据单位、范围和分类依据说明。

## Example

### Scenario

盐分等级 Code Editor 图例

Source: `raw_GEE_case/GEE教程_MOD44W印度土壤盐分可视化.md`

### Implementation

```javascript
var classes = [
  {color: '2c7bb6', label: 'Non saline'},
  {color: 'abd9e9', label: 'Slightly saline'},
  {color: 'ffffbf', label: 'Moderately saline'},
  {color: 'fdae61', label: 'Highly saline'},
  {color: 'd7191c', label: 'Extremely saline'}
];
```

### Validation

Status: `optional` operation; knowledge status follows frontmatter and requires Task-level execution evidence.

### Limitations

该片段只定义展示配置。等级阈值必须另有数据依据，`ui.*` 不受当前无头 worker 支持。
