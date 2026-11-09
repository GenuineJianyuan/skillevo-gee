---
id: SUBTASK-PHENOLOGY-THRESHOLD-CLASSIFY-001
kind: subtask
title: EVI Percentile-Threshold Phenological-Stage Classification
version: 0.1.0
status: experimental
summary: Combine EVI levels and growth direction to label green-up, maturity, senescence, and dormancy using rules.
tags: [phenology, percentile, rule-classification]
references: []
source: raw_GEE_case EVI phenological-stage classification tutorial
operation: required
---

# Purpose

Classify phenological stages using regional/temporal percentile thresholds and rising/falling states.

## Operation classification

`required`. This operation is part of the core analysis workflow of its owning Task.

## Procedure

Calculate low and high EVI thresholds. During rising periods, distinguish green-up and maturity using the low/high interval; during falling periods, distinguish senescence and dormancy using the high threshold. Output a discrete class band.

## Constraints

- Validate thresholds by crop, region, and year; do not directly transfer values from the source example.
- Class masks should be mutually exclusive, with no-data and unclassified pixels defined explicitly.
- A modal time series describes only the dominant class and may hide spatial heterogeneity.

## Example

### Scenario

EVI Direction and Percentile-Based Phenology Rules

Source: raw_GEE_case EVI phenological-stage classification tutorial

### Implementation

```javascript
var stage = ee.Image(0)
  .where(growing.and(evi.gt(lower)).and(evi.lte(upper)), 1)
  .where(growing.and(evi.gt(upper)), 2)
  .where(growing.not().and(evi.gt(upper)), 3)
  .where(growing.not().and(evi.lte(upper)), 4)
  .rename('phenological_stage');
```

### Validation

Status: `required` operation; knowledge status follows frontmatter and requires Task-level execution evidence.

### Limitations

Define class 0 as unclassified rather than a valid stage. Calibrate percentile parameters using regional samples or literature.
