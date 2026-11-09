---
id: SUBTASK-TIMESERIES-TABLE-EXPORT-001
kind: subtask
title: Convert Image-Collection Regional Statistics to a Time-Series Table
version: 0.1.0
status: experimental
summary: Reduce an image collection by region for each observation, retain dates and values, and prepare the result for CSV export.
tags: [time-series, reduce-region, feature-collection, csv]
references: []
source: raw_GEE_case ERA5 wind-speed time-series and CSV-export tutorial
operation: required
---

# Purpose

Convert an image collection into a FeatureCollection containing dates, statistics, and quality information.

## Operation classification

`required`. This operation is part of the core analysis workflow of its owning Task.

## Procedure

Read `system:time_start` from each image, reduce over the target region, write dates and values into geometry-free Features, then export the table.

## Constraints

- Specify reduction scale, projection, and region semantics.
- Do not cast null values directly to `ee.Number`; retain or filter them and record the reason.
- Export is asynchronous; successful submission does not mean export completion.

## Example

### Scenario

Regional Wind-Speed Statistics and CSV Export

Source: raw_GEE_case ERA5 wind-speed time-series and CSV-export tutorial

### Implementation

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

### Validation

Status: `required` operation; knowledge status follows frontmatter and requires Task-level execution evidence.

### Limitations

Filter or flag null values and monitor the asynchronous export task. The current demo worker does not support `Export`.
