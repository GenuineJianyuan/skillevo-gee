---
id: SUBTASK-CLIMATE-WATER-BALANCE-001
kind: subtask
title: Monthly Precipitation and PET Water Balance
version: 0.1.0
status: experimental
summary: Aggregate precipitation and potential-evapotranspiration collections by month and calculate the P-PET water balance.
tags: [chirps, terraclimate, monthly, water-balance]
references: []
source: raw_GEE_case CHIRPS and TerraClimate drought-index tutorial
operation: required
---

# Purpose

Align daily CHIRPS precipitation with TerraClimate PET, aggregate by explicit year-month, and calculate water balance.

## Operation classification

`required`. This operation is part of the core analysis workflow of its owning Task.

## Procedure

Filter and sum each year-month separately, align band names, units, projection semantics, and time properties, then calculate `P - PET`.

## Constraints

- Do not combine the same month across multiple years into one image unless the goal is a multi-year monthly climatology.
- Apply the PET scale factor before subtraction; half-open temporal intervals are preferable.
- Months in the two collections must correspond one-to-one, and empty collections must be checked.

## Example

### Scenario

Monthly Water Balance from CHIRPS and TerraClimate

Source: raw_GEE_case CHIRPS and TerraClimate drought-index tutorial

### Implementation

```javascript
function monthlySum(collection, year, month, outputBand) {
  var start = ee.Date.fromYMD(year, month, 1);
  return collection.filterDate(start, start.advance(1, 'month'))
    .sum().rename(outputBand)
    .set({'year': year, 'month': month, 'system:time_start': start.millis()});
}
var balance = precipitationMonth.subtract(petMonth).rename('water_balance');
```

### Validation

Status: `required` operation; knowledge status follows frontmatter and requires Task-level execution evidence.

### Limitations

The source tutorial sums by month across years, which may lose the year-month series. A production implementation must iterate explicitly over year-month pairs and verify the PET scale factor.
