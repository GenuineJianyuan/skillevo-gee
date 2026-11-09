---
id: SUBTASK-TERRACLIMATE-SOIL-PREPROCESS-001
kind: subtask
title: TerraClimate Soil-Moisture Filtering and Preprocessing
version: 0.1.0
status: experimental
summary: Filter the TerraClimate soil band by region and period, apply catalog-defined scaling, and preserve temporal properties.
tags: [terraclimate, soil-moisture, preprocessing]
references: []
source: raw_GEE_case TerraClimate soil-moisture analysis tutorial
operation: required
---

# Purpose

Construct a soil-moisture image collection with explicit region, time, units, and quality status.

## Operation classification

`required`. This operation is part of the core analysis workflow of its owning Task.

## Procedure

Load TerraClimate, select `soil`, filter by a half-open date range, apply the scale factor from the data catalog, clip to the target geometry, and copy temporal properties.

## Constraints

- Administrative-area selection must not rely solely on the implicit union returned by cross-continent multi-point `filterBounds`.
- Read scale factors and units from the current product catalog; do not rely exclusively on tutorial constants.
- Check collection size, temporal coverage, and valid pixels first.

## Example

### Scenario

Preprocess the TerraClimate Soil Band

Source: raw_GEE_case TerraClimate soil-moisture analysis tutorial

### Implementation

```javascript
var soil = ee.ImageCollection('IDAHO_EPSCOR/TERRACLIMATE')
  .filterBounds(aoi).filterDate(start, end).select('soil')
  .map(function(image) {
    return image.multiply(scaleFactor).clip(aoi)
      .copyProperties(image, ['system:time_start']);
  });
```

### Validation

Status: `required` operation; knowledge status follows frontmatter and requires Task-level execution evidence.

### Limitations

`scaleFactor` must come from the current data catalog; the source example's `0.1` is recorded only as a value requiring verification.
