---
id: SUBTASK-GEE-IMAGE-LOAD-001
kind: subtask
title: Load a fixed Earth Engine image
version: 1.0.0
status: verified
summary: Construct an ee.Image from a known Earth Engine asset ID and select scenario-appropriate bands.
tags: [gee, data-access, image]
references: []
source: reference-demo/script_320013.txt
verified_at: 2026-11-02T11:30:59+08:00
operation: required
---

# Purpose

Load a fixed Earth Engine image by asset ID. The asset must be accessible to the
configured project and must contain the bands required by downstream steps.

## Operation classification

`required`. This operation is part of the core analysis workflow of its owning Task.

## Procedure

Use `ee.Image(asset_id)`, then select or visualize only bands whose semantics,
scale, and value range are known for the product.

## Constraints

- Confirm asset existence and access permission before planning downstream work.
- Do not transfer visualization min/max values across products without checking units.
- Record product version and acquisition identity for reproducibility.

## Example

### Scenario

Load a Fixed Landsat 8 Image

Source: reference demo `script_320013.txt` (implementation embedded below)

### Implementation

```javascript
var image = ee.Image('LANDSAT/LC08/C02/T1_TOA/LC08_044034_20140318');
Map.setCenter(-122.37383, 37.6193, 15);
```

### Validation

The existing GEE worker successfully loaded this fixed image and returned valid-pixel statistics for B4/B3/B2.

### Limitations

This Example validates only the loading of a fixed asset and pixel availability. It does not establish that the dataset is suitable for other study regions,
periods, or scientific questions. Recheck bands, units, and access permissions when changing products.
