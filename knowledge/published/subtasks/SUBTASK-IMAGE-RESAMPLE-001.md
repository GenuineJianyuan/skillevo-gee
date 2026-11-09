---
id: SUBTASK-IMAGE-RESAMPLE-001
kind: subtask
title: Apply bicubic resampling to continuous imagery
version: 1.0.0
status: verified
summary: Request bicubic resampling for an Earth Engine image before downstream reprojection or reduction.
tags: [gee, resampling, bicubic]
references: []
source: reference-demo/script_320013.txt
verified_at: 2026-11-02T11:30:59+08:00
operation: required
---

# Purpose

Apply `image.resample('bicubic')` when continuous imagery should use bicubic
interpolation during the next reprojection.

## Operation classification

`required`. This operation is part of the core analysis workflow of its owning Task.

## Procedure

Earth Engine defers computation. `resample('bicubic')` changes the interpolation
method used by the next reprojection rather than eagerly creating a new raster.

## Constraints

- Do not apply bicubic interpolation to categorical labels or integer class maps.
- Interpret the effect together with the downstream projection and scale.
- Edge values may change and interpolation can introduce values outside the local input range.

## Example

### Scenario

The example loads a fixed Landsat 8 Collection 2 image near San Francisco,
creates a bicubic-resampled variant, and adds diagnostic layers. The worker
turns layers into bounded regional evaluations.

Source: reference demo `script_320013.txt` (implementation embedded below).

### Implementation

The implementation is embedded here so the Subtask remains self-contained:

```javascript
var landsat = ee.Image(
  'LANDSAT/LC08/C02/T1_TOA/LC08_044034_20160323'
);

var visParams = {
  bands: ['B4', 'B3', 'B2'],
  min: 0,
  max: 0.3
};

Map.addLayer(landsat, visParams, 'Original image');

// The next reprojection uses bicubic interpolation.
var resampled = landsat.resample('bicubic');

Map.addLayer(resampled, visParams, 'Resampled image');
```

### Validation

- Runtime: Earth Engine JavaScript SDK `1.7.31` through Node.js.
- Validation date: 2026-11-02.
- Result: three cloud evaluations succeeded, zero failed.
- Evidence: three successful cloud evaluations recorded during the 2026-11-02
  reference-environment verification.

### Limitations

This is a runtime and audit-path fixture. It is not a complete scientific Task,
does not perform export, and does not establish optimal resampling choices.
