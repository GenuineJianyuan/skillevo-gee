---
id: SUBTASK-COLLECTION-FILTER-001
kind: subtask
title: 加载并过滤 Earth Engine 影像集合
version: 0.1.0
status: experimental
summary: 按产品、波段、AOI 和半开时间范围构建非空影像集合，并保留后续分析所需属性。
tags: [data-access, image-collection, filter]
references: []
source: raw_GEE_case
operation: required
---

# Purpose

为分析方法提供经过身份、波段、时间和空间检查的输入集合。

## Operation classification

`required`。凡 Task 依赖 ImageCollection，必须先完成数据加载与过滤。

## Procedure

使用明确数据集 ID 创建集合，选择精确波段，按 AOI 和 `[start, end)` 时间范围过滤，应用必要的比例因子和 QA，并检查集合大小与首幅影像波段。

## Constraints

不得使用可能选择多组语义的宽泛正则；产品版本、缩放因子和 QA 必须依据当前目录；空集合必须阻断后续代码。

## Example

### Scenario

加载指定时期和区域的 TerraClimate PET。

### Implementation

```javascript
var collection = ee.ImageCollection('IDAHO_EPSCOR/TERRACLIMATE')
  .filterBounds(aoi)
  .filterDate(start, end)
  .select('pet');
print('collection_size', collection.size());
```

### Validation

验证集合大小、首末时间、波段名、单位和 AOI 内有效像元。

### Limitations

集合存在不代表适合当前科学问题；产品更换时必须重新核验参数。
