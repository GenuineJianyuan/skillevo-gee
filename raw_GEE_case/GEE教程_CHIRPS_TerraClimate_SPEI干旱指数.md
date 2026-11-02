# GEE教程：基于 CHIRPS 和 TerraClimate 数据计算 SPEI 干旱指数

- 作者：生态云计算
- 发布时间：2025年4月8日 08:00
- 原文：https://mp.weixin.qq.com/s?__biz=MzkwOTI5MjE5NA==&mid=2247496288&idx=1&sn=7775714aa2b49533d53cf490b19d2c06

## 简介

本文演示如何使用 GEE 计算标准化降水蒸散指数 (SPEI)。SPEI 同时考虑降水和潜在蒸散量 (PET)，比仅基于降水的指数更全面地反映干旱状况。

## 工作流程

1. 定义感兴趣区域。
2. 设置研究时段。
3. 加载 CHIRPS 降水和 TerraClimate PET 数据。
4. 计算月度总和。
5. 计算月度水量平衡（P - PET）。
6. 标准化水量平衡以创建 SPEI。
7. 过滤并可视化指定月份的 SPEI。
8. 将结果导出到 Google Drive。

## 完整代码

~~~javascript
var aoi = ee.FeatureCollection("FAO/GAUL/2015/level0")
  .filterBounds(geometry);
Map.addLayer(aoi);
Map.centerObject(geometry, 4);

var startyear = 2019;
var endyear = 2023;
var startmonth = 1;
var endmonth = 12;
var start_date = ee.Date.fromYMD(startyear, startmonth, 1);
var end_date = ee.Date.fromYMD(endyear, endmonth, 30);
var years = ee.List.sequence(startyear, endyear);
var months = ee.List.sequence(startmonth, endmonth);

var precip = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
  .filterDate(start_date, end_date)
  .select('precipitation');
var pet = ee.ImageCollection("IDAHO_EPSCOR/TERRACLIMATE")
  .filterDate(start_date, end_date)
  .select('pet');
print('precip', precip);
print('pet', pet);

var calculateMonthlySum = function(imageCollection, bandName) {
  return ee.ImageCollection(
    ee.List.sequence(1, 12).map(function(month) {
      var monthly = imageCollection
        .filter(ee.Filter.calendarRange(month, month, 'month'))
        .sum()
        .set('month', month);
      return monthly.rename(bandName + '_monthly');
    })
  );
};

var precipMonthly = calculateMonthlySum(precip, 'precipitation');
var petMonthly = calculateMonthlySum(pet, 'pet');

var waterBalance = precipMonthly.map(function(image) {
  var month = image.get('month');
  var petImage = petMonthly.filter(ee.Filter.eq('month', month)).first();
  return image.subtract(petImage)
    .rename('water_balance').set('month', month);
});

// 简化标准化，仅用于演示
var standardize = function(image) {
  var mean = ee.Image(waterBalance.reduce(ee.Reducer.mean()));
  var stdDev = ee.Image(waterBalance.reduce(ee.Reducer.stdDev()));
  return image.subtract(mean).divide(stdDev).rename('SPEI');
};

var speiCollection = waterBalance.map(standardize);
print('speiCollection', speiCollection);
var SPEI_Months = speiCollection.filter(
  ee.Filter.calendarRange(1, 3, 'month')
);
Map.addLayer(
  speiCollection,
  {min: -2, max: 2, palette: ['red', 'yellow', 'green']},
  'SPEI'
);

Export.image.toDrive({
  image: SPEI_Months.mean().clip(aoi),
  description: 'SPEI',
  scale: 250,
  region: aoi,
  maxPixels: 8e13,
  fileFormat: 'GeoTIFF'
});
~~~

> 原文说明：标准化通常需要将水量平衡拟合到概率分布，再转换为标准正态分布；代码采用简化标准化，仅用于演示。

## 结果

![全球SPEI干旱指数结果](https://mmbiz.qpic.cn/sz_mmbiz_png/zWpoXAeaXBquHReyrKWXlZvicZyiaBDs0PpdsrBxBNxWsxSDu1IWibtCwHKTYo8XbLugAkk0aahU8mqvZy2SKZaMQ/640?wx_fmt=png&from=appmsg#imgIndex=0)

## 代码说明

- 感兴趣区域使用 FAO/GAUL/2015/level0 国家边界数据。
- 时间范围设置为 2019–2023 年。
- CHIRPS 提供降水数据，TerraClimate 提供 PET 数据。
- 按月份聚合数据，计算 P - PET 水量平衡。
- 使用均值和标准差执行简化标准化。
- 筛选 1–3 月 SPEI，并将平均结果导出为 GeoTIFF。

> 注：内容从公开微信公众号页面提取，代码排版已按 Markdown 整理；版权归原作者所有。
