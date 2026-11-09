---
id: SUBTASK-THEMATIC-LEGEND-001
kind: subtask
title: GEE Thematic Classification and Legend
version: 0.1.0
status: experimental
summary: Build thematic layers and a Code Editor legend from validated class thresholds and colors.
tags: [visualization, legend, ui]
references: []
source: raw_GEE_case soil-salinity visualization tutorial
operation: optional
---

# Purpose

Map scientifically defined classes to colors and display a legend in the GEE Code Editor.

## Operation classification

`optional`. This operation affects only presentation or delivery; it does not change core analysis results.

## Procedure

Maintain ordered threshold-label-color tuples. Generate map styling and the legend from the same configuration to prevent inconsistencies.

## Constraints

- `ui.*` is available only in the Code Editor and is not supported by the current UI-less execution worker.
- The number of classes, thresholds, and colors must be consistent.
- A legend does not replace explanations of data units, ranges, or classification rationale.

## Example

### Scenario

Soil-Salinity Class Legend in the Code Editor

Source: raw_GEE_case soil-salinity visualization tutorial

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

This snippet defines presentation settings only. Class thresholds require separate data-based justification, and `ui.*` is not supported by the current headless worker.
