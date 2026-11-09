---
id: SUBTASK-SALINITY-LAND-MASK-001
kind: subtask
title: Load Salinity Data and Apply a Land Mask
version: 0.1.0
status: experimental
summary: Combine a soil-salinity raster with a water product, mask water areas, and clip to the study region.
tags: [soil-salinity, water-mask, clip]
references: []
source: raw_GEE_case MOD44W India soil-salinity visualization tutorial
operation: required
---

# Purpose

Generate a salinity layer containing only land areas.

## Operation classification

`required`. This operation is part of the core analysis workflow of its owning Task.

## Procedure

After validating the AOI and salinity asset, select an explicit water-product band and encoding, construct a Boolean land mask, apply it to the salinity summary image, and clip the result.

## Constraints

- Private and community assets require access and stability checks.
- Explain the temporal dimension of the salinity collection and the meaning of `median()`.
- The water-product version, period, and class encoding must match the study objective.

## Example

### Scenario

Combine Salinity Layers with a MOD44W Land Mask

Source: raw_GEE_case MOD44W India soil-salinity visualization tutorial

### Implementation

```javascript
var salinity = ee.ImageCollection(salinityAsset).median();
var water = ee.ImageCollection(waterAsset).filterDate(start, end)
  .select('water_mask').mosaic();
var landSalinity = salinity.updateMask(water.eq(0)).clip(aoi);
```

### Validation

Status: `required` operation; knowledge status follows frontmatter and requires Task-level execution evidence.

### Limitations

Check asset permissions, product version, `water_mask` encoding, and salinity-data units first.
