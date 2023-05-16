# eastmoney

东方财富行业研报，每天自动更新

## 环境

Python 3.11.3
pip 22.3.1

## 安装依赖

cd 到项目目录,执行下面命令
```bash
pip install -r requirements.txt
```
## 用法
```python
from eastmoney import EastMoneyReport

# 行业研报存放的路径,你可以任意写，我这里目录是'D:/行业研报/'
reportHelper = EastMoneyReport('D:/行业研报')

"""
下载指定行业研报
:param industry_code_list: 数组类型 ,比如 ['*', '1030', '1045']
:param pageSize: 一页多少个数据
:param pageNo: 页码 从1开始
:param beginTime: 开始时间 比如: 2020-05-16
:param endTime: 结束时间 比如: 2023-05-16
:param is_download_pdf: 是否下载pdf研报，默认False不下载
:return: None
"""
reportHelper.download_report(['*', '1030', '1045'], pageSize=10, is_download_pdf=True)
```
- `industry_code_list` 字符串数组类型，里面是`行业代码`，比如你要下载金融行业研报,你就传['474'],
上面的例子中传递的是['*', '1030', '1045']，所以查询是`全行业`，`电机`，`房地产服务`，三个行业研报。
[点击我查询行业代码](industry.csv) 

# 注意
防止给东财服务器造成流量压力，请酌情使用，不然回头人家给你接口封了，大家都没得用了。

# 研报目录
每天会自动更新一次研报目录，但是不包括研报PDF文件，如需pdf研报，请自行下载, 或者调用上面的方法下载

[`全行业`](gen/全行业/全行业.csv)  [`玻璃玻纤`](gen/玻璃玻纤/玻璃玻纤.csv)  [`通用设备`](gen/通用设备/通用设备.csv)  [`综合行业`](gen/综合行业/综合行业.csv)  [`化学制品`](gen/化学制品/化学制品.csv)  [`游戏`](gen/游戏/游戏.csv)  [`房地产服务`](gen/房地产服务/房地产服务.csv)  [`生物制品`](gen/生物制品/生物制品.csv)  [`玻璃玻纤`](gen/玻璃玻纤/玻璃玻纤.csv)  [`半导体`](gen/半导体/半导体.csv)  [`包装材料`](gen/包装材料/包装材料.csv)  [`保险`](gen/保险/保险.csv)  [`采掘行业`](gen/采掘行业/采掘行业.csv)  [`船舶制造`](gen/船舶制造/船舶制造.csv)  [`电子化学品`](gen/电子化学品/电子化学品.csv)  [`电源设备`](gen/电源设备/电源设备.csv)  [`电池`](gen/电池/电池.csv)  [`电机`](gen/电机/电机.csv)  [`多元金融`](gen/多元金融/多元金融.csv)  [`电网设备`](gen/电网设备/电网设备.csv)  [`电子元件`](gen/电子元件/电子元件.csv)  [`电力行业`](gen/电力行业/电力行业.csv)  [`房地产服务`](gen/房地产服务/房地产服务.csv)  [`风电设备`](gen/风电设备/风电设备.csv)  [`非金属材料`](gen/非金属材料/非金属材料.csv)  [`房地产开发`](gen/房地产开发/房地产开发.csv)  [`纺织服装`](gen/纺织服装/纺织服装.csv)  [`光学光电子`](gen/光学光电子/光学光电子.csv)  [`光伏设备`](gen/光伏设备/光伏设备.csv)  [`工程机械`](gen/工程机械/工程机械.csv)  [`贵金属`](gen/贵金属/贵金属.csv)  [`工程咨询服务`](gen/工程咨询服务/工程咨询服务.csv)  [`钢铁行业`](gen/钢铁行业/钢铁行业.csv)  [`公用事业`](gen/公用事业/公用事业.csv)  [`工程建设`](gen/工程建设/工程建设.csv)  [`化学制品`](gen/化学制品/化学制品.csv)  [`化学原料`](gen/化学原料/化学原料.csv)  [`化肥行业`](gen/化肥行业/化肥行业.csv)  [`环保行业`](gen/环保行业/环保行业.csv)  [`航运港口`](gen/航运港口/航运港口.csv)  [`航空机场`](gen/航空机场/航空机场.csv)  [`互联网服务`](gen/互联网服务/互联网服务.csv)  [`化学制药`](gen/化学制药/化学制药.csv)  [`航天航空`](gen/航天航空/航天航空.csv)  [`化纤行业`](gen/化纤行业/化纤行业.csv)  [`教育`](gen/教育/教育.csv)  [`计算机设备`](gen/计算机设备/计算机设备.csv)  [`家用轻工`](gen/家用轻工/家用轻工.csv)  [`家电行业`](gen/家电行业/家电行业.csv)  [`交运设备`](gen/交运设备/交运设备.csv)  [`旅游酒店`](gen/旅游酒店/旅游酒店.csv)  [`美容护理`](gen/美容护理/美容护理.csv)  [`贸易行业`](gen/贸易行业/贸易行业.csv)  [`煤炭行业`](gen/煤炭行业/煤炭行业.csv)  [`能源金属`](gen/能源金属/能源金属.csv)  [`农药兽药`](gen/农药兽药/农药兽药.csv)  [`酿酒行业`](gen/酿酒行业/酿酒行业.csv)  [`农牧饲渔`](gen/农牧饲渔/农牧饲渔.csv)  [`汽车整车`](gen/汽车整车/汽车整车.csv)  [`汽车服务`](gen/汽车服务/汽车服务.csv)  [`汽车零部件`](gen/汽车零部件/汽车零部件.csv)  [`燃气`](gen/燃气/燃气.csv)  [`软件开发`](gen/软件开发/软件开发.csv)  [`生物制品`](gen/生物制品/生物制品.csv)  [`塑料制品`](gen/塑料制品/塑料制品.csv)  [`商业百货`](gen/商业百货/商业百货.csv)  [`石油行业`](gen/石油行业/石油行业.csv)  [`食品饮料`](gen/食品饮料/食品饮料.csv)  [`水泥建材`](gen/水泥建材/水泥建材.csv)  [`通用设备`](gen/通用设备/通用设备.csv)  [`通信服务`](gen/通信服务/通信服务.csv)  [`铁路公路`](gen/铁路公路/铁路公路.csv)  [`通信设备`](gen/通信设备/通信设备.csv)  [`物流行业`](gen/物流行业/物流行业.csv)  [`文化传媒`](gen/文化传媒/文化传媒.csv)  [`消费电子`](gen/消费电子/消费电子.csv)  [`小金属`](gen/小金属/小金属.csv)  [`橡胶制品`](gen/橡胶制品/橡胶制品.csv)  [`游戏`](gen/游戏/游戏.csv)  [`医药商业`](gen/医药商业/医药商业.csv)  [`医疗器械`](gen/医疗器械/医疗器械.csv)  [`医疗服务`](gen/医疗服务/医疗服务.csv)  [`有色金属`](gen/有色金属/有色金属.csv)  [`银行`](gen/银行/银行.csv)  [`仪器仪表`](gen/仪器仪表/仪器仪表.csv)  [`综合行业`](gen/综合行业/综合行业.csv)  [`专业服务`](gen/专业服务/专业服务.csv)  [`中药`](gen/中药/中药.csv)  [`专用设备`](gen/专用设备/专用设备.csv)  [`珠宝首饰`](gen/珠宝首饰/珠宝首饰.csv)  [`装修装饰`](gen/装修装饰/装修装饰.csv)  [`证券`](gen/证券/证券.csv)  [`装修建材`](gen/装修建材/装修建材.csv)  [`造纸印刷`](gen/造纸印刷/造纸印刷.csv)  