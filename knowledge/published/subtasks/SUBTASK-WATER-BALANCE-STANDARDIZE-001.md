---
id: SUBTASK-WATER-BALANCE-STANDARDIZE-001
kind: subtask
title: Water-Balance Standardization and Drought Outputs
version: 0.1.0
status: experimental
summary: Standardize the water-balance series, select target periods, and prepare map or export outputs.
tags: [drought-index, standardization, export]
references: []
source: raw_GEE_case CHIRPS and TerraClimate drought-index tutorial
operation: required
---

# Purpose

Transform the water-balance series into comparable indicators and produce summaries for specified months.

## Operation classification

`required`. This operation is part of the core analysis workflow of its owning Task.

## Procedure

The experimental Example uses `(x-mean)/stdDev`. A rigorous SPEI requires an accumulation scale, probability-distribution fitting, and standard-normal transformation and must be clearly identified as a different implementation.

## Constraints

- Stop or mark results invalid when standard deviation is zero or the sample is too short.
- Do not label a simplified z-score as a rigorously validated SPEI result.
- Use a geometry, not an unprocessed FeatureCollection, for the export region and check task status.

## Example

### Scenario

Water-Balance Z-Score Demonstration

Source: raw_GEE_case CHIRPS and TerraClimate drought-index tutorial

### Implementation

```javascript
var mean = waterBalance.mean();
var stdDev = waterBalance.reduce(ee.Reducer.stdDev());
var standardized = waterBalance.map(function(image) {
  return image.subtract(mean).divide(stdDev)
    .rename('water_balance_z')
    .copyProperties(image, ['system:time_start']);
});
```

### Validation

Status: `required` operation; knowledge status follows frontmatter and requires Task-level execution evidence.

### Limitations

This is a z-score and must not be named rigorous SPEI. Explicitly handle short series and zero-standard-deviation pixels.
