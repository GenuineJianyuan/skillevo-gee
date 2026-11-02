---
id: SUBTASK-TERRACLIMATE-SOIL-PREPROCESS-001
kind: subtask
title: TerraClimate 土壤湿度过滤与预处理
version: 0.1.0
status: experimental
summary: 按区域和时间过滤 TerraClimate soil 波段，应用目录定义的缩放并保留时间属性。
tags: [terraclimate, soil-moisture, preprocessing]
references: []
source: raw_GEE_case/GEE训练教程_TerraClimate土壤湿度分析.md
---

# 简述

构造具有明确区域、时间、单位和质量状态的土壤湿度影像集合。

## 算法描述

加载 TerraClimate，选择 `soil`，使用半开日期区间过滤，依据数据目录应用比例因子，裁剪到目标几何并复制时间属性。

## 软约束

- 行政区选择不能仅依赖跨洲多点 `filterBounds` 后的隐式并集。
- 比例因子和单位应从当前产品目录读取，不以教程常数为唯一依据。
- 先检查集合大小、时间覆盖和有效像元。

## Example

### TerraClimate soil 波段预处理

- Source: `raw_GEE_case/GEE训练教程_TerraClimate土壤湿度分析.md`
- Status: `experimental`

# 代码骨架

```javascript
var soil = ee.ImageCollection('IDAHO_EPSCOR/TERRACLIMATE')
  .filterBounds(aoi).filterDate(start, end).select('soil')
  .map(function(image) {
    return image.multiply(scaleFactor).clip(aoi)
      .copyProperties(image, ['system:time_start']);
  });
```

# 限制

`scaleFactor` 必须来自当前数据目录；原案例的 `0.1` 仅作为待核验来源记录。
