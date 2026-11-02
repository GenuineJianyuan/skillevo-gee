# GEE训练教程：计算 1980–2020 特定区域风速、生成时序图并导出 CSV

- 作者：生态云计算
- 发布时间：2025年4月7日 08:00
- 原文：https://mp.weixin.qq.com/s?__biz=MzkwOTI5MjE5NA==&mid=2247496278&idx=6&sn=4ebf25be96401fcc3728ebebb9dfc727

## 使用 Google Earth Engine 计算风速并导出数据

本文介绍使用 GEE 计算特定区域风速、生成时间序列图表以及将历史风速数据导出为 CSV 文件。

## 1. 定义感兴趣区域（ROI）

~~~javascript
var roi = ee.FeatureCollection([
  ee.Feature(ee.Geometry.Point([-118.0076171875, 40.84542567752384]), {"system:index":"0"}),
  ee.Feature(ee.Geometry.Point([-109.3064453125, 41.04458705851143]), {"system:index":"1"}),
  ee.Feature(ee.Geometry.Point([-98.6716796875, 37.99445972919209]), {"system:index":"2"}),
  // 省略其它点……
  ee.Feature(ee.Geometry.Point([-117.7439453125, 46.43636768451249]), {"system:index":"15"})
]);
~~~

## 2. 计算风速

~~~javascript
function calculateWindSpeed(img) {
  var windSpeed = img.expression('sqrt((u**2) + (v**2))', {
    'u': img.select('u_.*'),
    'v': img.select('v_.*')
  }).rename('wind_speed');
  return windSpeed.copyProperties(img, img.propertyNames());
}

var era5 = ee.ImageCollection("ECMWF/ERA5/DAILY")
  .select('u_.*', 'v_.*')
  .filterDate('2010', '2024');
var windspeedCurrent = era5.map(calculateWindSpeed);
~~~

## 3. 显示风速时间序列图表

~~~javascript
print(ui.Chart.image.series({
  imageCollection: windspeedCurrent,
  region: roi,
  reducer: ee.Reducer.mean(),
  scale: 27000,
  xProperty: 'system:time_start'
}).setOptions({
  title: 'Wind Speed Time Series (2010–2024)',
  vAxis: {title: 'Wind Speed (m/s)'},
  hAxis: {title: 'Date'}
}));
~~~

## 4. 处理历史风速数据

~~~javascript
var wind40 = ee.ImageCollection("ECMWF/ERA5/DAILY")
  .select('u_.*', 'v_.*')
  .filterDate('1980', '2020');
var windspeedHistorical = wind40.map(calculateWindSpeed);
~~~

## 5. 提取风速和日期值

~~~javascript
function extractValues(image) {
  var date = ee.Date(image.get('system:time_start')).format('YYYY-MM-dd');
  var value = ee.Number(image.reduceRegion({
    reducer: ee.Reducer.mean(), geometry: roi, scale: 27000
  }).get('wind_speed'));
  return ee.Feature(null, {'date': date, 'windspeed': value});
}
~~~

## 6. 导出历史风速数据

~~~javascript
var windFeatureCollection = ee.FeatureCollection(
  windspeedHistorical.map(extractValues)
);
Export.table.toDrive({
  collection: windFeatureCollection,
  description: 'windspeed40',
  fileFormat: 'CSV'
});
~~~

## 全部代码

~~~javascript
var roi = ee.FeatureCollection([
  ee.Feature(ee.Geometry.Point([-118.0076171875, 40.84542567752384]), {"system:index":"0"}),
  ee.Feature(ee.Geometry.Point([-109.3064453125, 41.04458705851143]), {"system:index":"1"}),
  ee.Feature(ee.Geometry.Point([-98.6716796875, 37.99445972919209]), {"system:index":"2"}),
  ee.Feature(ee.Geometry.Point([-100.5173828125, 35.60196174346124]), {"system:index":"3"}),
  ee.Feature(ee.Geometry.Point([-109.9216796875, 33.868621305661506]), {"system:index":"4"}),
  ee.Feature(ee.Geometry.Point([-117.3923828125, 36.948164829456]), {"system:index":"5"}),
  ee.Feature(ee.Geometry.Point([-81.26933593750002, 34.01445071534518]), {"system:index":"6"}),
  ee.Feature(ee.Geometry.Point([-88.12480468750002, 32.91467130080992]), {"system:index":"7"}),
  ee.Feature(ee.Geometry.Point([-83.55449218750002, 41.90066866763205]), {"system:index":"8"}),
  ee.Feature(ee.Geometry.Point([-75.46855468750002, 38.54647536763548]), {"system:index":"9"}),
  ee.Feature(ee.Geometry.Point([-92.43144531250002, 41.572744699288165]), {"system:index":"10"}),
  ee.Feature(ee.Geometry.Point([-88.56425781250002, 39.90807865441729]), {"system:index":"11"}),
  ee.Feature(ee.Geometry.Point([-94.9802734375, 45.827293480505276]), {"system:index":"12"}),
  ee.Feature(ee.Geometry.Point([-102.0994140625, 46.678111874978136]), {"system:index":"13"}),
  ee.Feature(ee.Geometry.Point([-111.0642578125, 45.949647228511985]), {"system:index":"14"}),
  ee.Feature(ee.Geometry.Point([-117.7439453125, 46.43636768451249]), {"system:index":"15"})
]);

function calculateWindSpeed(img) {
  var windSpeed = img.expression('sqrt((u**2) + (v**2))', {
    'u': img.select('u_.*'), 'v': img.select('v_.*')
  }).rename('wind_speed');
  return windSpeed.copyProperties(img, img.propertyNames());
}

var era5 = ee.ImageCollection("ECMWF/ERA5/DAILY")
  .select('u_.*', 'v_.*').filterDate('2010', '2024');
var windspeedCurrent = era5.map(calculateWindSpeed);
print(ui.Chart.image.series({
  imageCollection: windspeedCurrent, region: roi,
  reducer: ee.Reducer.mean(), scale: 27000,
  xProperty: 'system:time_start'
}).setOptions({
  title: 'Wind Speed Time Series (2010–2024)',
  vAxis: {title: 'Wind Speed (m/s)'}, hAxis: {title: 'Date'}
}));

var wind40 = ee.ImageCollection("ECMWF/ERA5/DAILY")
  .select('u_.*', 'v_.*').filterDate('1980', '2020');
var windspeedHistorical = wind40.map(calculateWindSpeed);

function extractValues(image) {
  var date = ee.Date(image.get('system:time_start')).format('YYYY-MM-dd');
  var value = ee.Number(image.reduceRegion({
    reducer: ee.Reducer.mean(), geometry: roi, scale: 27000
  }).get('wind_speed'));
  return ee.Feature(null, {'date': date, 'windspeed': value});
}

var windFeatureCollection = ee.FeatureCollection(
  windspeedHistorical.map(extractValues)
);
Export.table.toDrive({
  collection: windFeatureCollection,
  description: 'windspeed40', fileFormat: 'CSV'
});
~~~

## 结果

![风速时序图表可视化](https://mmbiz.qpic.cn/sz_mmbiz_png/zWpoXAeaXBqVyxbottib1IBXBYfruOeIksuiasjukHz7eiaHFgNboEibas4NNrK7fGKhicJJXGxJon8AUmYNRBz17vQ/640?wx_fmt=png&from=appmsg#imgIndex=0)

> 注：内容从公开微信公众号页面提取，代码排版已按 Markdown 整理；版权归原作者所有。
