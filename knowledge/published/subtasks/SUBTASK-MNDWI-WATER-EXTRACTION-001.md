---
id: SUBTASK-MNDWI-WATER-EXTRACTION-001
kind: subtask
title: Landsat MNDWI 水体提取
version: 0.1.0
status: experimental
summary: 使用绿光与短波红外波段计算 MNDWI，并按阈值生成水体掩膜。
tags: [landsat, mndwi, water-mask]
references: []
source: raw_GEE_case/GEE训练教程_Landsat8_MODIS水域面积变化时序图表.md
---

# 简述

对经过云处理的 Landsat 影像计算 MNDWI，并生成研究区水体候选掩膜。

## 算法描述

计算 `(green - swir1) / (green + swir1)`，根据经过验证的阈值分类，并保留指数和水体掩膜。

## 软约束

- 先完成云、阴影和无效像元掩膜；中值合成会改变时序含义。
- 阈值受浑浊度、建筑和阴影影响，需要区域验证。
- 不同 Landsat 产品的波段名和缩放方式不同。

## Example

### Landsat 8 MNDWI 水体掩膜

- Source: `raw_GEE_case/GEE训练教程_Landsat8_MODIS水域面积变化时序图表.md`
- Status: `experimental`

# 代码骨架

```javascript
function addWaterMask(image) {
  var mndwi = image.normalizedDifference(['B3', 'B6']).rename('MNDWI');
  return image.addBands([mndwi, mndwi.gt(threshold).rename('water')]);
}
```

# 限制

原教程只按 `CLOUD_COVER < 1` 过滤且随后多年取中值；正式时序任务需要逐期云/阴影掩膜和阈值验证。
