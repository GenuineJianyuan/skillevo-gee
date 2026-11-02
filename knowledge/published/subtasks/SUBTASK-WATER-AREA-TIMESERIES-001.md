---
id: SUBTASK-WATER-AREA-TIMESERIES-001
kind: subtask
title: 水体掩膜面积与时间序列
version: 0.1.0
status: experimental
summary: 将逐期水体掩膜乘以像元面积，并按区域求和得到平方公里序列。
tags: [water-area, pixel-area, time-series]
references: []
source: raw_GEE_case/GEE训练教程_Landsat8_MODIS水域面积变化时序图表.md
---

# 简述

从每期水体掩膜计算区域水域总面积，而不是水体面积影像的均值。

## 算法描述

对指数应用产品适配阈值，生成布尔掩膜，乘 `pixelArea()/1e6` 后用 `sum` 归约到 ROI，并保留时间属性。

## 软约束

- 指数比例因子和阈值必须与产品定义一致。
- `mean` 归约不代表总面积；必须使用 `sum` 并明确 km2。
- 需要处理云、积雪、缺测和岸线混合像元。

## Example

### MODIS 水体像元面积求和

- Source: `raw_GEE_case/GEE训练教程_Landsat8_MODIS水域面积变化时序图表.md`
- Status: `experimental`

# 代码骨架

```javascript
var rows = ndwiCollection.map(function(image) {
  var waterArea = image.gte(threshold).selfMask()
    .multiply(ee.Image.pixelArea()).divide(1e6).rename('water_km2');
  var total = waterArea.reduceRegion({
    reducer: ee.Reducer.sum(), geometry: roi, scale: scale, maxPixels: 1e9
  }).get('water_km2');
  return ee.Feature(null, {date: image.date().format('YYYY-MM-dd'), water_km2: total});
});
```

# 限制

原教程的阈值 `>=1` 和 `ui.Chart.image.series(... mean ...)` 不能直接作为总面积算法使用。
