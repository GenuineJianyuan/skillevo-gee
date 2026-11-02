# GEE训练教程——使用 Google Earth Engine 分析特定区域的土壤湿度

- 作者：生态云计算
- 发布时间：2025年4月14日 08:00
- 原文：https://mp.weixin.qq.com/s?__biz=MzkwOTI5MjE5NA==&mid=2247496358&idx=1&sn=617adb2d4dc953e9c6bf09d8e88f8ae9

## 使用 Google Earth Engine 分析土壤湿度

本文介绍如何使用 GEE 获取、处理和可视化特定区域的土壤湿度数据。

## 代码概述

~~~javascript
var geometry = ee.Geometry.MultiPoint([
  [-88.47636718750002, 13.237841991972566],
  [50.840821455582564, 18.806730172889836]
]);
var country = ee.FeatureCollection("FAO/GAUL/2015/level0")
  .filterBounds(geometry);
Map.addLayer(country);
Map.centerObject(geometry, 3);
~~~

首先定义表示感兴趣区域的几何图形，然后从 FAO GAUL 数据集中获取国家边界并添加到地图。

## 获取土壤湿度数据

~~~javascript
var Soilmoisture = ee.ImageCollection("IDAHO_EPSCOR/TERRACLIMATE")
  .select('soil')
  .filterBounds(country)
  .filterDate('2009-01-01', '2010-12-20');

Soilmoisture = Soilmoisture.map(function(img) {
  return img.clip(country)
    .multiply(0.1).subtract(0).add(0)
    .copyProperties(img, ['system:time_start']);
});

print(Soilmoisture.size());
Map.addLayer(Soilmoisture.mean(), {
  min: 0,
  max: 2,
  palette: [
    '#00007f', '#0000ff', '#007fff', '#00ffff', '#7fff7f',
    '#ffff00', '#ff7f00', '#ff0000', '#7f0000'
  ]
}, 'Soilmoisture');
~~~

数据来自 IDAHO EPSCOR TerraClimate，选择 soil 波段，按国家边界和日期过滤，对影像裁剪和单位转换，并添加平均土壤湿度图层。

## 创建时间序列图表

~~~javascript
print(ui.Chart.image.series({
  imageCollection: Soilmoisture,
  region: country,
  reducer: ee.Reducer.mean(),
  scale: 4638.3,
  xProperty: 'system:time_start'
}).setSeriesNames(['Soilmoisture Growth']).setOptions({
  title: 'Soilmoisture Growth',
  hAxis: {title: 'Year'},
  vAxis: {title: '(mm)'},
  interpolateNulls: true,
  lineWidth: 1,
  pointSize: 2,
  curveType: 'function'
}));
~~~

## 添加图例

~~~javascript
var legend = ui.Panel({
  style: {position: 'bottom-right', padding: '8px 13px'}
});
var legendTitle = ui.Label({
  value: 'Soilmoisture Growth',
  style: {
    fontWeight: 'bold', fontSize: '18px',
    margin: '0 0 4px 0', padding: '0'
  }
});
legend.add(legendTitle);

var makeColorBar = function(palette) {
  return ui.Thumbnail({
    image: ee.Image.pixelLonLat().select(1),
    params: {
      bbox: [0, 0, 0.1, 1], dimensions: '10x100',
      format: 'png', min: 0, max: 1, palette: palette
    },
    style: {stretch: 'vertical', margin: '8px 0'}
  });
};

var palette = [
  '#00007f', '#0000ff', '#007fff', '#00ffff', '#7fff7f',
  '#ffff00', '#ff7f00', '#ff0000', '#7f0000'
];
var minLabel = ui.Label({value: '172', style: {margin: '4px 8px'}});
var maxLabel = ui.Label({value: '162', style: {margin: '4px 8px'}});
legend.add(minLabel);
legend.add(makeColorBar(palette));
legend.add(maxLabel);
Map.add(legend);
~~~

## 总结

代码展示了在 GEE 中获取、处理、可视化土壤湿度数据和绘制时间序列的方法。

## 结果

![土壤湿度可视化结果](https://mmbiz.qpic.cn/sz_mmbiz_png/zWpoXAeaXBor5GJjc8g7Oj2fsKmAgOWRqKoibgBTeBL0lUj9ibQWnO9sL5lqHpdl0OiczrEh1icbQ2dKTdRZlZj4icA/640?wx_fmt=png&from=appmsg#imgIndex=0)

> 注：内容从公开微信公众号页面提取，代码排版已按 Markdown 整理；版权归原作者所有。
