---
id: SUBTASK-SALINITY-LAND-MASK-001
kind: subtask
title: 盐分数据加载与陆地掩膜
version: 0.1.0
status: experimental
summary: 将土壤盐分栅格与水体产品组合，屏蔽水域后裁剪到研究区。
tags: [soil-salinity, water-mask, clip]
references: []
source: raw_GEE_case/GEE教程_MOD44W印度土壤盐分可视化.md
---

# 简述

生成仅保留陆地区域的盐分图层。

## 算法描述

验证 AOI 和盐分资产后，对水体产品选择明确波段及编码，构建陆地布尔掩膜，应用到盐分统计影像并裁剪。

## 软约束

- 私有和社区资产需要权限与稳定性检查。
- 盐分集合的时间维度和 `median()` 含义必须说明。
- 水体产品的版本、时间和分类编码必须匹配研究目的。

## Example

### 盐分图层与 MOD44W 陆地掩膜组合

- Source: `raw_GEE_case/GEE教程_MOD44W印度土壤盐分可视化.md`
- Status: `experimental`

# 代码骨架

```javascript
var salinity = ee.ImageCollection(salinityAsset).median();
var water = ee.ImageCollection(waterAsset).filterDate(start, end)
  .select('water_mask').mosaic();
var landSalinity = salinity.updateMask(water.eq(0)).clip(aoi);
```

# 限制

资产权限、产品版本、`water_mask` 编码和盐分数据单位均需先查询验证。
