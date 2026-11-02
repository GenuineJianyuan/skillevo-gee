---
id: SUBTASK-WATER-BALANCE-STANDARDIZE-001
kind: subtask
title: 水量平衡标准化与干旱结果输出
version: 0.1.0
status: experimental
summary: 对水量平衡序列进行标准化，筛选目标时段并准备地图或导出结果。
tags: [drought-index, standardization, export]
references: []
source: raw_GEE_case/GEE教程_CHIRPS_TerraClimate_SPEI干旱指数.md
---

# 简述

将水量平衡序列转换为可比较指标，并生成指定月份的汇总结果。

## 算法描述

实验例采用 `(x-mean)/stdDev`。严格 SPEI 需要积累尺度、概率分布拟合和标准正态变换，应作为不同实现明确标注。

## 软约束

- 标准差为零或样本过短时必须终止或标记无效。
- 不能把简化 z-score 标为严格 SPEI 验证结果。
- 导出区域应使用几何而非未经处理的 FeatureCollection，并检查任务状态。

## Example

### 水量平衡 z-score 演示

- Source: `raw_GEE_case/GEE教程_CHIRPS_TerraClimate_SPEI干旱指数.md`
- Status: `experimental`

# 代码骨架

```javascript
var mean = waterBalance.mean();
var stdDev = waterBalance.reduce(ee.Reducer.stdDev());
var standardized = waterBalance.map(function(image) {
  return image.subtract(mean).divide(stdDev)
    .rename('water_balance_z')
    .copyProperties(image, ['system:time_start']);
});
```

# 限制

这是 z-score，不应命名为严格 SPEI。短序列和零标准差像元需要显式处理。
