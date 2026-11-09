---
id: SUBTASK-WIND-SPEED-DERIVATION-001
kind: subtask
title: Derive Wind Speed from Horizontal Components
version: 0.1.0
status: experimental
summary: Calculate wind speed as sqrt(u^2+v^2) from u and v components and preserve temporal properties.
tags: [era5, wind, vector-magnitude]
references: []
source: raw_GEE_case ERA5 wind-speed time-series and CSV-export tutorial
operation: required
---

# Purpose

Convert horizontal wind components with the same height and temporal-statistic definition into scalar wind speed.

## Operation classification

`required`. This operation is part of the core analysis workflow of its owning Task.

## Procedure

Select one explicit u/v band pair per image, calculate `sqrt(u.pow(2)+v.pow(2))`, rename it `wind_speed`, and copy temporal properties.

## Constraints

- Do not use broad regular expressions that may match multiple heights.
- Both components must share units, grid, and temporal-statistic definition.
- Verify that the ERA5 dataset ID remains available in the catalog.

## Example

### Scenario

Wind-Speed Calculation from ERA5 u/v Components

Source: raw_GEE_case ERA5 wind-speed time-series and CSV-export tutorial

### Implementation

```javascript
function addWindSpeed(image) {
  var u = image.select('u_component_of_wind_10m');
  var v = image.select('v_component_of_wind_10m');
  return u.pow(2).add(v.pow(2)).sqrt().rename('wind_speed')
    .copyProperties(image, ['system:time_start']);
}
```

### Validation

Status: `required` operation; knowledge status follows frontmatter and requires Task-level execution evidence.

### Limitations

Band names are semantic examples; use the current catalog for the selected ERA5 product. Do not use `u_.*` or `v_.*` to implicitly match multiple components.
