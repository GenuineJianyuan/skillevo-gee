---
id: SUBTASK-AOI-DEFINE-001
kind: subtask
title: Define and Validate the Analysis Region
version: 0.1.0
status: experimental
summary: Convert user geometry, point sets, or administrative-boundary assets into a semantically explicit AOI for filtering, clipping, and reduction.
tags: [aoi, geometry, boundary]
references: []
source: raw_GEE_case
operation: required
---

# Purpose

Establish an explicit study region for subsequent data filtering and spatial computation.

## Operation classification

`required`. All current business Tasks depend on a spatial extent; map centering and boundary display are not required parts of this operation.

## Procedure

Read user geometry or an accessible boundary asset and check geometry type, validity, and spatial semantics. Merge or buffer when necessary, then output a single AOI geometry.

## Constraints

Do not implicitly treat multiple administrative areas returned by a cross-region, multi-point `filterBounds` as the target region. Verify access to private assets first; specify buffer distance and projection.

## Example

### Scenario

Select country boundaries from GAUL that intersect the user geometry.

### Implementation

```javascript
var candidates = ee.FeatureCollection('FAO/GAUL/2015/level0')
  .filterBounds(userGeometry);
var aoi = candidates.geometry();
```

### Validation

Check candidate count, AOI area, boundary extent, and semantic consistency with the user's target.

### Limitations

Intersection filtering is not equivalent to name-based administrative-area selection; cross-country or disconnected regions require user confirmation.
