# GEE 教程：基于 MODIS/006/MOD44W 数据的印度地区土壤盐分可视化

- 作者：生态云计算
- 发布时间：2025年4月11日 08:00
- 原文：https://mp.weixin.qq.com/s?__biz=MzkwOTI5MjE5NA==&mid=2247496314&idx=1&sn=a92c002b6ddeac37420bf9e8c76ba28c

## 简介

这篇博客指导使用 Google Earth Engine (GEE) 可视化印度地区的土壤盐分数据，并创建自定义图例。

## 流程

1. 加载感兴趣区域 (AOI)：使用印度地区的多边形矢量数据。
2. 加载 GEE 公开的全球土壤盐分数据集。
3. 加载 MODIS 水体掩膜，屏蔽水体，只显示陆地盐分数据。
4. 创建用于解释土壤盐分等级的自定义图例。
5. 处理土壤盐分数据，并使用自定义调色板添加到地图。

![可视化结果](https://mmbiz.qpic.cn/sz_mmbiz_png/zWpoXAeaXBoIsD56APvDqAZmJ2iaibPE9xQb1VDFWLicS7ZibPfRx3YXMsvjpoVjlRLUMT4dMZ9ZQaPKWN2DEvjaHg/640?wx_fmt=png&from=appmsg#imgIndex=0)

## 数据

MODIS/006/MOD44W 数据由 NASA 的 MODIS（中分辨率成像光谱仪）提供，可用于监测和分析全球覆盖变化，并评估其对气候变化和生态系统服务的影响。文章介绍其空间分辨率为 0.01 度 × 0.01 度，可用于土地利用、生态系统健康、气候变化和灾后生态恢复研究。

## 代码实现

~~~javascript
// 1. 加载感兴趣区域 (AOI)
var aoi = ee.FeatureCollection(
  'projects/ee-niasmasis/assets/Shapefiles/IND_Districts'
);
Map.centerObject(aoi, 5);

// 2. 加载土壤盐分数据集
var soilSalinity = ee.ImageCollection(
  "projects/sat-io/open-datasets/global_soil_salinity"
);

// 3. 加载 MODIS 水体掩膜数据集
var dataset = ee.ImageCollection('MODIS/006/MOD44W')
  .filter(ee.Filter.date('2015-01-01', '2015-05-01'));
var waterMask = dataset.select('water_mask');

// 4. 创建图例
var legend = ui.Panel({
  style: {position: 'bottom-left', padding: '8px 15px'}
});
var legendTitle = ui.Label({
  value: 'Legend',
  style: {
    fontWeight: 'bold', fontSize: '18px',
    margin: '0 0 4px 0', padding: '0'
  }
});
legend.add(legendTitle);

var makeRow = function(color, name) {
  var colorBox = ui.Label({
    style: {
      backgroundColor: '#' + color,
      padding: '8px', margin: '0 0 4px 0'
    }
  });
  var description = ui.Label({
    value: name, style: {margin: '0 0 4px 6px'}
  });
  return ui.Panel({
    widgets: [colorBox, description],
    layout: ui.Panel.Layout.Flow('horizontal')
  });
};

var palette = ['2c7bb6', 'abd9e9', 'ffffbf', 'fdae61', 'd7191c'];
var names = [
  'Non saline', 'Slightly saline', 'Moderately saline',
  'Highly saline', 'Extremely saline'
];
for (var i = 0; i < 5; i++) {
  legend.add(makeRow(palette[i], names[i]));
}
Map.add(legend);

// 5. 添加土壤盐分图层
var salinityLayer = soilSalinity.median()
  .updateMask(waterMask.mosaic().eq(0))
  .clip(aoi);
Map.addLayer(
  salinityLayer,
  {min: 0, max: 5, palette: palette},
  'Soil Salinity'
);
~~~

> 注：内容从公开微信公众号页面提取，代码排版已按 Markdown 整理；版权归原作者所有。
