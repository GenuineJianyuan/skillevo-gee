---
id: SUBTASK-REGION-STATS-001
kind: subtask
title: Audit an image with bounded regional statistics
version: 1.0.0
status: verified
summary: Evaluate mean, minimum, maximum, and valid-pixel count over a small region to confirm real GEE computation.
tags: [gee, audit, reduce-region, statistics]
references: []
source: src/gee/runtime/worker.js
verified_at: 2026-11-02T11:30:59+08:00
operation: required
---

# Purpose

Use a deliberately small region to check that an image produces real pixels and
plausible summary values, rather than treating metadata access as execution proof.

## Operation classification

`required`. This operation is part of the core analysis workflow of its owning Task.

## Procedure

Combine mean, min/max, and count reducers in one `reduceRegion` request. Record
the geometry, scale, CRS, selected bands, and `maxPixels` bound.

## Constraints

- The region must intersect valid data.
- Scale and CRS must be meaningful for the product and diagnostic purpose.
- Non-empty statistics are an execution check, not a scientific validation.

## Example

### Scenario

Multi-Statistic GEE Audit over a Small Region

Source: `src/gee/runtime/worker.js`

### Implementation

```javascript
var stats = image.reduceRegion({
  reducer: ee.Reducer.mean()
    .combine({reducer2: ee.Reducer.minMax(), sharedInputs: true})
    .combine({reducer2: ee.Reducer.count(), sharedInputs: true}),
  geometry: ee.Geometry.Point(center).buffer(radius),
  scale: scale,
  crs: 'EPSG:3857',
  maxPixels: 100000
});
```

### Validation

The existing worker has successfully run equivalent checks for original, resampled, and NDVI layers, with zero cloud-side failures.

### Limitations

Small-region statistics demonstrate only that computable pixels exist within the specified geometry. They do not replace full spatial-coverage checks,
accuracy validation, scale-sensitivity analysis, or evaluation of the scientific meaning of results.
