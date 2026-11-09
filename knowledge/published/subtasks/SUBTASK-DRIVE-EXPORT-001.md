---
id: SUBTASK-DRIVE-EXPORT-001
kind: subtask
title: Export Analysis Results to Google Drive
version: 0.1.0
status: experimental
summary: Submit image or table results as asynchronous Drive Export tasks when the user explicitly requests file delivery.
tags: [export, drive, geotiff, csv]
references: []
source: raw_GEE_case
operation: optional
---

# Purpose

Convert analysis results that passed acceptance checks into external file-delivery tasks.

## Operation classification

`optional`. Export is not required to calculate indicators or validate results; enable it only when the user requests files.

## Procedure

Choose `Export.image.toDrive` or `Export.table.toDrive` based on output type. Set region, scale, CRS, fields, and file format, and record the task description.

## Constraints

Successful submission does not mean the task completed. `region` must be a geometry. Do not export before validating core results. The current headless worker does not monitor asynchronous Export tasks.

## Example

### Scenario

Export a date-value table as CSV.

### Implementation

```javascript
Export.table.toDrive({
  collection: rows,
  description: exportName,
  fileFormat: 'CSV'
});
```

### Validation

Before submission, check that the collection is non-empty, fields exist, and values are valid. After submission, monitor status with an executor that supports asynchronous tasks.

### Limitations

The current project can generate export code only; task submission must not be treated as successful file delivery.
