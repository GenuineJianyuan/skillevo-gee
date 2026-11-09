---
id: SUBTASK-MNDWI-WATER-EXTRACTION-001
kind: subtask
title: Landsat MNDWI Water Extraction
version: 0.1.0
status: experimental
summary: Calculate MNDWI from green and shortwave-infrared bands and generate a water mask using a threshold.
tags: [landsat, mndwi, water-mask]
references: []
source: raw_GEE_case Landsat 8 and MODIS surface-water time-series tutorial
operation: required
---

# Purpose

Calculate MNDWI from cloud-screened Landsat imagery and generate a candidate water mask for the study region.

## Operation classification

`required`. This operation is part of the core analysis workflow of its owning Task.

## Procedure

Calculate `(green - swir1) / (green + swir1)`, classify using a validated threshold, and retain both the index and water mask.

## Constraints

- Apply cloud, shadow, and invalid-pixel masks first; a median composite changes temporal semantics.
- Thresholds are affected by turbidity, built-up areas, and shadows and require regional validation.
- Band names and scaling differ across Landsat products.

## Example

### Scenario

Landsat 8 MNDWI Water Mask

Source: raw_GEE_case Landsat 8 and MODIS surface-water time-series tutorial

### Implementation

```javascript
function addWaterMask(image) {
  var mndwi = image.normalizedDifference(['B3', 'B6']).rename('MNDWI');
  return image.addBands([mndwi, mndwi.gt(threshold).rename('water')]);
}
```

### Validation

Status: `required` operation; knowledge status follows frontmatter and requires Task-level execution evidence.

### Limitations

The source tutorial filters only on `CLOUD_COVER < 1` and then takes a multi-year median. A production time-series Task requires per-observation cloud/shadow masking and threshold validation.
