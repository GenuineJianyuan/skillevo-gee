---
id: SUBTASK-DRIVE-EXPORT-001
kind: subtask
title: 将分析结果导出到 Google Drive
version: 0.1.0
status: experimental
summary: 在用户明确要求交付文件时，将影像或表格结果提交为异步 Drive Export 任务。
tags: [export, drive, geotiff, csv]
references: []
source: raw_GEE_case
operation: optional
---

# Purpose

把已通过分析验收的结果转换为外部文件交付任务。

## Operation classification

`optional`。导出不是计算指标和验证结果的必要步骤，仅在用户要求文件时启用。

## Procedure

根据输出类型选择 `Export.image.toDrive` 或 `Export.table.toDrive`，设置 region、scale、CRS、字段和文件格式，并记录任务描述。

## Constraints

导出提交成功不等于任务完成；region 必须是 geometry；不得在核心结果未验证前导出；当前 headless worker 尚不监测异步 Export。

## Example

### Scenario

导出日期—数值表为 CSV。

### Implementation

```javascript
Export.table.toDrive({
  collection: rows,
  description: exportName,
  fileFormat: 'CSV'
});
```

### Validation

提交前检查集合非空、字段存在、无非法值；提交后由支持异步任务的执行器监测状态。

### Limitations

当前项目只能生成导出代码，不能把任务提交视为已成功交付文件。
