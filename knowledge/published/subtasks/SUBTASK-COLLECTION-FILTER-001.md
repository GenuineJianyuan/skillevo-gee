---
id: SUBTASK-COLLECTION-FILTER-001
kind: subtask
title: Load and Filter an Earth Engine Image Collection
version: 0.2.0
status: experimental
summary: Build a non-empty image collection by product, band, AOI, and half-open date range while preserving attributes needed downstream.
tags: [data-access, image-collection, filter]
references: []
source: raw_GEE_case
operation: required
---

# Purpose

Provide an input collection checked for product identity, bands, temporal range, and spatial extent.

## Operation classification

`required`. Data loading and filtering must be completed before any Task that depends on an ImageCollection.

## Procedure

Create the collection from an explicit dataset ID, select exact bands, filter by AOI and `[start, end)`, apply required scale factors and QA, and check collection size and the first image's bands.

## Constraints

Do not use broad regular expressions that may select multiple semantic groups. Verify product version, scale factors, and QA against the current catalog. An empty collection must stop downstream code.

For the published water-area Task, use an official Collection 6.1 surface-reflectance product containing both `sur_refl_b04` (green) and `sur_refl_b02` (near infrared), such as `MODIS/061/MYD09A1` or `MODIS/061/MOD09A1`. Compute and rename the normalized difference to `NDWI`. Do not call `.select('NDWI')` on `MOD13A1` or `MOD13Q1`: they have no direct NDWI band and lack the required green band. Do not use the obsolete tutorial collection `MODIS/MYD09GA_006_NDWI` as a runtime dataset.

## Example

### Scenario

Load TerraClimate PET for a specified period and region.

### Implementation

```javascript
var collection = ee.ImageCollection('IDAHO_EPSCOR/TERRACLIMATE')
  .filterBounds(aoi)
  .filterDate(start, end)
  .select('pet');
print('collection_size', collection.size());
```

### Validation

Validate collection size, first and last timestamps, band names, units, and valid pixels within the AOI.

### Limitations

The existence of a collection does not establish its suitability for the scientific question. Revalidate parameters whenever the product changes.

### Published water-area specialization

```javascript
var ndwiCollection = ee.ImageCollection('MODIS/061/MYD09A1')
  .filterBounds(roi)
  .filterDate(start, end)
  .select(['sur_refl_b04', 'sur_refl_b02'])
  .map(function(image) {
    var ndwi = image.normalizedDifference(['sur_refl_b04', 'sur_refl_b02'])
      .rename('NDWI');
    return ndwi.copyProperties(image, ['system:time_start']);
  });
print('ndwi_collection_size', ndwiCollection.size());
print('ndwi_bands', ndwiCollection.first().bandNames());
```

Both reflectance bands share the same scale factor, so it cancels in the normalized difference. Apply the product QA mask before index calculation when the requested scientific quality requires it.
