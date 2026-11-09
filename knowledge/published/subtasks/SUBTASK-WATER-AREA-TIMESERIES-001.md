---
id: SUBTASK-WATER-AREA-TIMESERIES-001
kind: subtask
title: Water-Mask Area and Time Series
version: 0.2.0
status: experimental
summary: Multiply each observation's water mask by pixel area and sum by region to obtain an area series in square kilometers.
tags: [water-area, pixel-area, time-series]
references: []
source: raw_GEE_case Landsat 8 and MODIS surface-water time-series tutorial
operation: required
---

# Purpose

Calculate total regional surface-water area from each observation's water mask rather than taking the mean of a water-area image.

## Operation classification

`required`. This operation is part of the core analysis workflow of its owning Task.

## Procedure

Apply a product-appropriate threshold to the index, generate a Boolean mask, multiply by `pixelArea()/1e6`, reduce with `sum` over the ROI, and preserve temporal properties.

When monthly output is requested, first calculate each observation's total area, then group observations by calendar month and apply an explicitly stated statistic such as median. Emit one feature per requested month, include the valid-observation count, and retain null for an empty month rather than silently interpolating it.

## Constraints

- Index scale factors and thresholds must match the product definition.
- For NDWI derived with `normalizedDifference`, use a threshold in the normalized `[-1, 1]` domain. The source tutorial's `>= 1` threshold belongs to its obsolete derived product and is invalid for this implementation.
- A `mean` reduction is not total area; use `sum` and specify km2.
- Handle clouds, snow, missing observations, and mixed shoreline pixels.

## Example

### Scenario

Sum MODIS Water-Pixel Areas

Source: raw_GEE_case Landsat 8 and MODIS surface-water time-series tutorial

### Implementation

```javascript
var threshold = 0; // starting value; justify or calibrate for the ROI
var rows = ndwiCollection.map(function(image) {
  var waterArea = image.select('NDWI').gte(threshold).selfMask()
    .multiply(ee.Image.pixelArea()).divide(1e6).rename('water_km2');
  var total = waterArea.reduceRegion({
    reducer: ee.Reducer.sum(), geometry: roi, scale: scale, maxPixels: 1e9
  }).get('water_km2');
  return ee.Feature(null, {date: image.date().format('YYYY-MM-dd'), water_km2: total});
});
```

### Validation

Status: `required` operation; knowledge status follows frontmatter and requires Task-level execution evidence.

### Limitations

The source tutorial's `>=1` threshold and `ui.Chart.image.series(... mean ...)` cannot be used directly as a total-area algorithm.
