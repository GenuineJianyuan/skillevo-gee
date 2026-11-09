---
id: SUBTASK-SOIL-MOISTURE-SUMMARY-001
kind: subtask
title: Soil-Moisture Spatial Summary and Regional Time Series
version: 0.1.0
status: experimental
summary: Generate a temporal-mean soil-moisture image and a time series from regional statistics for each observation.
tags: [soil-moisture, spatial-summary, time-series]
references: []
source: raw_GEE_case TerraClimate soil-moisture analysis tutorial
operation: required
---

# Purpose

Generate a spatial overview and regional statistics series from the preprocessed collection.

## Operation classification

`required`. This operation is part of the core analysis workflow of its owning Task.

## Procedure

Generate a map layer from the collection's temporal mean. Reduce each observation over the study region with an appropriate reducer and scale, retaining date, statistic, and valid-pixel information.

## Constraints

- Palette minimum/maximum values must be based on the data distribution or product range.
- Regional means may hide spatial heterogeneity; also record valid area or stratified results.
- Code Editor charts and UI legends are not audit outputs for a headless execution environment.

## Example

### Scenario

Soil-Moisture Spatial Mean and Regional Series

Source: raw_GEE_case TerraClimate soil-moisture analysis tutorial

### Implementation

```javascript
var meanImage = soil.mean();
var rows = soil.map(function(image) {
  var value = image.reduceRegion({
    reducer: ee.Reducer.mean(), geometry: aoi, scale: scale, maxPixels: 1e9
  }).get('soil');
  return ee.Feature(null, {date: image.date().format('YYYY-MM'), soil: value});
});
```

### Validation

Status: `required` operation; knowledge status follows frontmatter and requires Task-level execution evidence.

### Limitations

Determine map visualization ranges from statistics. Explain the spatial meaning of means over multiple countries or disconnected geometries.
