---
id: SUBTASK-TIMESERIES-TABLE-EXPORT-001
kind: subtask
title: 影像集合区域时间序列表格化
version: 0.1.0
status: experimental
summary: 对影像集合逐期执行区域归约，保存日期和值并准备 CSV 导出。
tags: [time-series, reduce-region, feature-collection, csv]
references: []
source: raw_GEE_case/GEE训练教程_ERA5风速时序与CSV导出.md
---

# 简述

把影像集合转换为包含日期、统计值和质量信息的 FeatureCollection。

## 算法描述

逐影像读取 `system:time_start`，对目标区域执行归约，将日期和值写入无几何 Feature，最后导出表格。

## 软约束

- 归约尺度、投影和区域含义必须明确。
- 空值不能直接强制转换为 `ee.Number`；应保留或过滤并记录原因。
- Export 是异步任务，提交成功不等于导出完成。

## Example

### 风速区域统计与 CSV 导出

- Source: `raw_GEE_case/GEE训练教程_ERA5风速时序与CSV导出.md`
- Status: `experimental`

# 代码骨架

```javascript
var rows = windCollection.map(function(image) {
  var stats = image.reduceRegion({
    reducer: ee.Reducer.mean(), geometry: roi, scale: scale, maxPixels: 1e8
  });
  return ee.Feature(null, {
    date: image.date().format('YYYY-MM-dd'),
    wind_speed: stats.get('wind_speed')
  });
});
Export.table.toDrive({collection: rows, description: name, fileFormat: 'CSV'});
```

# 限制

需要过滤或标记空值并监测异步导出任务；当前 demo worker 不支持 `Export`。
