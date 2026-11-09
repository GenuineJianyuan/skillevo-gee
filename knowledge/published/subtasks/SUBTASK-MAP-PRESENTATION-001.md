---
id: SUBTASK-MAP-PRESENTATION-001
kind: subtask
title: GEE Map, Chart, and Legend Presentation
version: 0.1.0
status: experimental
summary: Optionally add Code Editor map layers, time-series charts, or legends after completing the core analysis.
tags: [visualization, chart, legend, ui]
references: []
source: raw_GEE_case
operation: optional
---

# Purpose

Provide a presentation layer for human inspection without changing core analysis results.

## Operation classification

`optional`. Include this operation only when the user requests visualization or interactive presentation; headless execution and numeric results do not depend on it.

## Procedure

Set visualization parameters from validated output ranges, then add map layers, `ui.Chart`, or a legend consistent with the same classification configuration.

## Constraints

`ui.*` is not supported by the current headless worker. Legends and palettes must not replace units, thresholds, or scientific classification rationale. Presentation failures must not change analysis conclusions.

## Example

### Scenario

Display a regional time-series chart.

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

Check that displayed data match the core outputs, axis units are explicit, and missing values are not inadvertently interpolated.

### Limitations

Code Editor UI cannot serve as automated audit evidence.
