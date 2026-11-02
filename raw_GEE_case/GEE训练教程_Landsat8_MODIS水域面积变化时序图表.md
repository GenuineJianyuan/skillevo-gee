# GEE训练教程：使用使用Landsat 8和MODIS数据分析了特定区域的水域面积变化时序图表

- 作者：生态云计算
- 发布时间：2025年4月10日 08:00
- 原文：[微信公众号文章](https://mp.weixin.qq.com/s/7VCPtTl65M9yMB4cGfe06Q)

### 使用 Google Earth Engine (GEE) 分析水域面积变化

在这篇博客中，我们将介绍如何使用 Google Earth Engine (GEE) 分析特定区域的水域面积变化。我们将使用 Landsat 8 和 MODIS 数据，通过计算改进的归一化差异水体指数（MNDWI）和归一化差异水体指数（NDWI）来提取水域信息，并分析其时间序列变化。

#### 1. 定义感兴趣区域（ROI）

首先，我们定义了一个多边形作为感兴趣区域（ROI），即我们要分析的区域。这里我们选择了阿尔巴尼亚附近的一个区域：

```javascript
var geometry = ee.Geometry.Polygon(
  [[[20.427070127991943, 41.257003447164195],
    [20.427070127991943, 40.742935339286014],
    [21.284003721741943, 40.742935339286014],
    [21.284003721741943, 41.257003447164195]]], null, false);
```

为了更清晰地展示区域范围，我们还加载了该区域所在的国家边界：

```javascript
var country = ee.FeatureCollection("FAO/GAUL/2015/level0")
  .filterBounds(geometry);
Map.addLayer(country); // 将国家边界添加到地图
Map.centerObject(geometry, 10); // 将地图中心设置为该区域，缩放级别为10
```

#### 2. 加载 Landsat 8 影像并计算 MNDWI

我们使用 Landsat 8 的 TOA（大气顶部反射率）数据，过滤了 2010 年 1 月 1 日至 2022 年 12 月 31 日的影像，并选择了一些波段：

```javascript
var IMG = ee.ImageCollection("LANDSAT/LC08/C02/T1_TOA")
  .filterBounds(geometry)
  .filterDate('2010-01-01', '2022-12-31')
  .filterMetadata('CLOUD_COVER', 'less_than', 1)
  .median()
  .clip(geometry)
  .select('B1', 'B2', 'B3', 'B4', 'B5', 'B6');
```

接下来，我们定义了一个函数来计算改进的归一化差异水体指数（MNDWI），并提取水域信息：

```javascript
function MNDW_f(img) {
  var MNDWI = img.normalizedDifference(['B3', 'B6']).rename('MNDWI');
  return img.addBands(MNDWI).updateMask(MNDWI.gt(0));
}

var IMG_water = MNDW_f(IMG);
Map.addLayer(
  IMG_water.select('MNDWI'),
  {palette: ['blue']},
  'IMG_water'
);
```

#### 3. 加载 MODIS NDWI 数据并计算水域面积

我们使用 MODIS 的 NDWI 数据，过滤了 2010 年 1 月 1 日至 2022 年 12 月 31 日的影像，并对每幅影像进行了裁剪和单位转换：

```javascript
var NDwI = ee.ImageCollection("MODIS/MYD09GA_006_NDWI")
  .select('NDWI')
  .filterBounds(geometry)
  .filterDate('2010-01-01', '2022-12-31');

NDwI = NDwI.map(function(img) {
  return img.clip(geometry)
    .multiply(1)
    .divide(1)
    .add(0)
    .subtract(0)
    .copyProperties(img, img.propertyNames());
});
```

为了计算水域面积，我们定义了一个阈值（NDWI ≥ 1），并将符合条件的像素面积转换为平方公里：

```javascript
var NDwI_area = NDwI.map(function(img) {
  var thr = img.gte(1); // 阈值
  var mask = thr.updateMask(thr);
  var area = mask.multiply(ee.Image.pixelArea().divide(1e6)); // 转换为平方公里
  return area.copyProperties(img, img.propertyNames());
});
```

打印影像集合的大小以确认数据加载成功：

```javascript
print(NDwI_area.size());
```

#### 4. 创建水域面积时间序列图

为了分析水域面积随时间的变化，我们创建了一个时间序列图：

```javascript
print(
  ui.Chart.image.series(
    NDwI_area,
    geometry,
    ee.Reducer.mean(),
    463.313,
    'system:time_start'
  ).setOptions({
    title: '湖泊和水域面积 (km²)',
    interpolateNulls: true,
    lineWidth: 1,
    pointSize: 2,
    curveType: 'function',
    vAxis: {title: 'AREA NDWI (km²)'}
  })
);
```

#### 5. 添加图例

为了更直观地理解地图中的颜色条带，我们添加了一个图例：

```javascript
var palette = ['ffffff', 'fffcf7', 'fbfffa', 'blue'];
var vis = {min: '', max: '', palette: palette};
var nSteps = 10;

// 创建颜色条
function makeColorBarParams(palette) {
  return {
    bbox: [0, 0, nSteps, 0.1],
    dimensions: '10x100',
    format: 'png',
    min: 0,
    max: nSteps,
    palette: palette,
  };
}

var colorBar = ui.Thumbnail({
  image: ee.Image.pixelLonLat().select(0).int(),
  params: makeColorBarParams(vis.palette),
  style: {
    stretch: 'horizontal',
    margin: '0px 4px',
    maxHeight: '12px'
  },
});

// 创建图例标签
var legendLabels = ui.Panel({
  widgets: [
    ui.Label(vis.min, {margin: '4px 8px'}),
    ui.Label(
      ((vis.max - vis.min) / 2 + vis.min),
      {
        margin: '4px 8px',
        textAlign: 'center',
        stretch: 'horizontal'
      }
    ),
    ui.Label(vis.max, {margin: '4px 8px'})
  ],
  layout: ui.Panel.Layout.flow('horizontal')
});

// 图例标题
var legendTitle = ui.Label({
  value: 'AREA NDWI (km²)',
  style: {fontWeight: 'bold'}
});

// 将图例添加到地图
var legendPanel = ui.Panel([legendTitle, colorBar, legendLabels]);
Map.add(legendPanel);
```

### 总结

通过以上步骤，我们成功地使用 Google Earth Engine 分析了特定区域的水域面积变化。通过 MNDWI 和 NDWI 指数，我们提取了水域信息，并通过时间序列图展示了水域面积的动态变化。这些数据对于研究水资源管理、生态系统健康以及气候变化的影响具有重要意义。

## 结果

![NDWI可视化结果](https://mmbiz.qpic.cn/sz_mmbiz_png/zWpoXAeaXBrSMN31n56HMJyqhv6x1VNymlDOqq5UibvibSqYnXkoibU4vDCTxC3xPicuD9vxAqk8GQn4NMJ7WVZHLg/640?wx_fmt=png&from=appmsg#imgIndex=0)

> 注：本文内容从公开微信公众号页面提取，代码排版已按 Markdown 格式整理；文字、代码与图片版权归原作者所有。
