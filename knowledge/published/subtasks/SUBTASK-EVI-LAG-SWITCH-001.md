---
id: SUBTASK-EVI-LAG-SWITCH-001
kind: subtask
title: EVI Lag Matching and Growth-Direction Signal
version: 0.1.0
status: experimental
summary: Match each EVI image to an earlier observation and derive a growth-direction band from current and lagged values.
tags: [evi, temporal-join, lag, growing-season]
references: []
source: raw_GEE_case EVI phenological-stage classification tutorial
operation: required
---

# Purpose

Find the previous valid EVI observation within a specified window for each time step and determine whether the vegetation index is rising or falling.

## Operation classification

`required`. This operation is part of the core analysis workflow of its owning Task.

## Procedure

Use a temporal join with `maxDifference` and temporal ordering filters, select the nearest earlier image as the lag band, then compare current and lagged EVI.

## Constraints

- Apply quality masks and scale factors first.
- Do not call `first().rename()` when there is no matching image.
- Ratios are unstable when lagged values approach zero; differences or robust thresholds may be more appropriate.

## Example

### Scenario

Temporal Join for EVI Lags

Source: raw_GEE_case EVI phenological-stage classification tutorial

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

Apply quality masks and scale factors first; filter out images without a `previous` match.
