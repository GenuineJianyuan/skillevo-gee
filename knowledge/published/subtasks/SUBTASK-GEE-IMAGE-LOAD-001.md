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
---

# Summary

Load a fixed Earth Engine image by asset ID. The asset must be accessible to the
configured project and must contain the bands required by downstream steps.

## Algorithm

Use `ee.Image(asset_id)`, then select or visualize only bands whose semantics,
scale, and value range are known for the product.

## Soft constraints

- Confirm asset existence and access permission before planning downstream work.
- Do not transfer visualization min/max values across products without checking units.
- Record product version and acquisition identity for reproducibility.

## Example

### 固定 Landsat 8 影像加载

- Source: reference demo `script_320013.txt` (implementation embedded below)
- Status: `verified`

# 代码骨架

```javascript
var image = ee.Image('LANDSAT/LC08/C02/T1_TOA/LC08_044034_20140318');
Map.setCenter(-122.37383, 37.6193, 15);
```

# 验证

该固定影像已通过现有 GEE worker 成功加载，并对 B4/B3/B2 返回有效像元统计。
