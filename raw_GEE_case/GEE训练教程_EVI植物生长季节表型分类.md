# GEE训练教程：分析特定区域的植被指数（EVI），并进行植物生长季节的表型分类和时序可视化

- 作者：生态云计算
- 发布时间：2025年4月10日 08:00
- 原文：[微信公众号文章](https://mp.weixin.qq.com/s/G43enP222-dvki3NZhtfwQ)

## 使用 Google Earth Engine 进行植物生长季节的表型分类

在本篇博客中，我们将使用 Google Earth Engine (GEE) 来分析特定区域的植被指数（EVI），并进行植物生长季节的表型分类。通过以下步骤，我们将实现对植被生长阶段的识别和可视化。

## 一、定义感兴趣区域（AOI）

首先，我们定义一个感兴趣区域（AOI）和其他几何形状：

```javascript
var AOI = ee.Geometry.Point([-47.14746471955989, -16.604138097638092]),
    geometry2 = ee.Geometry.Point([-62.51404611932089, -16.2037636793537]),
    geometry4 = ee.FeatureCollection([
      ee.Feature(
        ee.Geometry.Polygon(
          [[[-62.37644796668283, -16.28331110695178],
            [-62.37644796668283, -16.39944337981606],
            [-62.24461202918283, -16.39944337981606],
            [-62.24461202918283, -16.28331110695178]]], null, false),
        {"system:index": "0"}
      )
    ]),
    table18 = ee.FeatureCollection("users/anmarkos/GANADERIA/DIVISIONES/Azucaro_po");
```

## 二、处理植被指数（EVI）

接下来，我们将应用平滑滤波器到选定的 EVI 数据集，并仅处理感兴趣区域以节省资源：

```javascript
var AOI = AOI.buffer(600).aside(Map.addLayer).aside(Map.centerObject);
var mask = ee.Image(1).clip(AOI);

var your_smoothed_VI = ee.ImageCollection("MODIS/061/MYD13Q1")
  .select('EVI')
  .filterDate('2024-01-01', '2025-01-01')
  .map(function(x) {
    return x.updateMask(mask);
  });
```

## 三、创建滞后波段

我们将创建一个新的波段，包含平滑后的 EVI 的滞后值，并设置相应的滞后天数：

```javascript
var lagdays = 20;

var lag = function(leftCollection, rightCollection, lagDays) {
  var filter = ee.Filter.and(
    ee.Filter.maxDifference({
      difference: 1000 * 60 * 60 * 24 * lagDays,
      leftField: 'system:time_start',
      rightField: 'system:time_start'
    }),
    ee.Filter.greaterThan({
      leftField: 'system:time_start',
      rightField: 'system:time_start'
    })
  );

  return ee.Join.saveAll({
    matchesKey: 'images',
    measureKey: 'delta_t',
    ordering: 'system:time_start',
    ascending: false,
  }).apply({
    primary: leftCollection,
    secondary: rightCollection,
    condition: filter
  });
};

var merge = function(image) {
  var merger = function(current, previous) {
    return ee.Image(previous).addBands(current);
  };
  return ee.ImageCollection.fromImages(image.get('images')).iterate(merger, image);
};

var lagged = lag(your_smoothed_VI, your_smoothed_VI, lagdays);

var GROW = ee.ImageCollection(lagged.map(function(image) {
  var laggedImages = ee.ImageCollection.fromImages(image.get('images'));
  return ee.Image(image).addBands(laggedImages.first().rename('Laged_EVI'));
}));
```

## 四、创建生长季节开关

我们创建一个开关，用于掩膜非生长季节的蒸散发数据：

```javascript
function addSWITCH(x) {
  return x.addBands(
    x.select('EVI')
      .divide(x.select('Laged_EVI'))
      .gt(1)
      .rename('Growing_Season')
  );
}

var SWITCH = GROW.map(addSWITCH);
```

## 五、识别感兴趣的百分位数

我们识别感兴趣的百分位数，以应用于平滑后的 EVI：

```javascript
var lower = your_smoothed_VI.reduce(ee.Reducer.percentile([20]));
var upper = your_smoothed_VI.reduce(ee.Reducer.percentile([28]));
```

## 六、分类植物生长阶段

我们定义一个函数来分类植物的生长阶段：

```javascript
function cross(x) {
  var greenup = x.select('EVI')
    .updateMask(x.select('Growing_Season').eq(1))
    .updateMask(x.select('EVI').gt(lower))
    .updateMask(x.select('EVI').lt(upper))
    .neq(-1000).int();

  var maturity = x.select('EVI')
    .updateMask(x.select('Growing_Season').eq(1))
    .updateMask(x.select('EVI').gt(upper))
    .neq(-1000).multiply(2).int();

  var senescence = x.select('EVI')
    .updateMask(x.select('Growing_Season').eq(0))
    .updateMask(x.select('EVI').gt(upper))
    .neq(-1000).multiply(3).int();

  var curing = x.select('EVI')
    .updateMask(x.select('Growing_Season').eq(0))
    .updateMask(x.select('EVI').lt(upper))
    .neq(-1000).multiply(4).int();

  var phenological_stage = ee.ImageCollection([
    greenup, maturity, senescence, curing
  ]).mosaic().rename('phenological_stage');

  return x.addBands(phenological_stage);
}

var phenol_classify = SWITCH.map(cross).aside(print);
```

## 七、可视化结果

最后，我们将结果可视化：

```javascript
print(ui.Chart.image.series(
  phenol_classify.select('phenological_stage'),
  mask.geometry(),
  ee.Reducer.mode(),
  250
));
```

## 全部代码

以下是完整的代码，用于在 Google Earth Engine 中进行植物生长季节的表型分类：

```javascript
// 定义感兴趣区域（AOI）和其他几何形状
var AOI = ee.Geometry.Point([-47.14746471955989, -16.604138097638092]),
    geometry2 = ee.Geometry.Point([-62.51404611932089, -16.2037636793537]),
    geometry4 = ee.FeatureCollection([
      ee.Feature(
        ee.Geometry.Polygon(
          [[[-62.37644796668283, -16.28331110695178],
            [-62.37644796668283, -16.39944337981606],
            [-62.24461202918283, -16.39944337981606],
            [-62.24461202918283, -16.28331110695178]]], null, false),
        {"system:index": "0"}
      )
    ]),
    table18 = ee.FeatureCollection("users/anmarkos/GANADERIA/DIVISIONES/Azucaro_po");

// 处理植被指数（EVI）
AOI = AOI.buffer(600).aside(Map.addLayer).aside(Map.centerObject);
var mask = ee.Image(1).clip(AOI);

var your_smoothed_VI = ee.ImageCollection("MODIS/061/MYD13Q1")
  .select('EVI')
  .filterDate('2024-01-01', '2025-01-01')
  .map(function(x) {
    return x.updateMask(mask);
  });

// 创建滞后波段
var lagdays = 20;
var lag = function(leftCollection, rightCollection, lagDays) {
  var filter = ee.Filter.and(
    ee.Filter.maxDifference({
      difference: 1000 * 60 * 60 * 24 * lagDays,
      leftField: 'system:time_start',
      rightField: 'system:time_start'
    }),
    ee.Filter.greaterThan({
      leftField: 'system:time_start',
      rightField: 'system:time_start'
    })
  );

  return ee.Join.saveAll({
    matchesKey: 'images',
    measureKey: 'delta_t',
    ordering: 'system:time_start',
    ascending: false,
  }).apply({
    primary: leftCollection,
    secondary: rightCollection,
    condition: filter
  });
};

var merge = function(image) {
  var merger = function(current, previous) {
    return ee.Image(previous).addBands(current);
  };
  return ee.ImageCollection.fromImages(image.get('images')).iterate(merger, image);
};

var lagged = lag(your_smoothed_VI, your_smoothed_VI, lagdays);
var GROW = ee.ImageCollection(lagged.map(function(image) {
  var laggedImages = ee.ImageCollection.fromImages(image.get('images'));
  return ee.Image(image).addBands(laggedImages.first().rename('Laged_EVI'));
}));

// 创建生长季节开关
function addSWITCH(x) {
  return x.addBands(
    x.select('EVI').divide(x.select('Laged_EVI')).gt(1).rename('Growing_Season')
  );
}
var SWITCH = GROW.map(addSWITCH);

// 识别感兴趣的百分位数
var lower = your_smoothed_VI.reduce(ee.Reducer.percentile([20]));
var upper = your_smoothed_VI.reduce(ee.Reducer.percentile([28]));

// 分类植物生长阶段
function cross(x) {
  var greenup = x.select('EVI').updateMask(x.select('Growing_Season').eq(1))
    .updateMask(x.select('EVI').gt(lower)).updateMask(x.select('EVI').lt(upper)).neq(-1000).int();
  var maturity = x.select('EVI').updateMask(x.select('Growing_Season').eq(1))
    .updateMask(x.select('EVI').gt(upper)).neq(-1000).multiply(2).int();
  var senescence = x.select('EVI').updateMask(x.select('Growing_Season').eq(0))
    .updateMask(x.select('EVI').gt(upper)).neq(-1000).multiply(3).int();
  var curing = x.select('EVI').updateMask(x.select('Growing_Season').eq(0))
    .updateMask(x.select('EVI').lt(upper)).neq(-1000).multiply(4).int();

  var phenological_stage = ee.ImageCollection([
    greenup, maturity, senescence, curing
  ]).mosaic().rename('phenological_stage');
  return x.addBands(phenological_stage);
}

var phenol_classify = SWITCH.map(cross).aside(print);

// 可视化结果
print(ui.Chart.image.series(
  phenol_classify.select('phenological_stage'),
  mask.geometry(),
  ee.Reducer.mode(),
  250
));
```

## 总结

通过以上步骤，我们成功地使用 Google Earth Engine 分析了植被指数，并对植物生长季节进行了表型分类。这种方法为研究特定区域的植物生长动态提供了强有力的工具。如果您对这个过程有任何问题或想法，请随时与我联系！

## 结果

![一个大豆区域的时序变化图](https://mmbiz.qpic.cn/sz_mmbiz_png/zWpoXAeaXBr3JKCuvTPvtRhp8FueHQ1iatSpAvHoAqU21I2ljYuQoicdHI8Gg2zS8VIdb26UPHjWLEFknGy9QjJg/640?wx_fmt=png&from=appmsg#imgIndex=0)

> 注：本文内容从公开微信公众号页面提取，代码排版已按 Markdown 格式整理；文字、代码与图片版权归原作者所有。
