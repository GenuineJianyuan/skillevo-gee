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
---

# Summary

Use a deliberately small region to check that an image produces real pixels and
plausible summary values, rather than treating metadata access as execution proof.

## Algorithm

Combine mean, min/max, and count reducers in one `reduceRegion` request. Record
the geometry, scale, CRS, selected bands, and `maxPixels` bound.

## Soft constraints

- The region must intersect valid data.
- Scale and CRS must be meaningful for the product and diagnostic purpose.
- Non-empty statistics are an execution check, not a scientific validation.

## Example

### 小区域多统计量 GEE 审计

- Source: `src/gee/runtime/worker.js`
- Status: `verified`

# 代码骨架

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

# 验证

现有 worker 已对原始、重采样和 NDVI 图层成功执行同类检查，云端失败数为零。
