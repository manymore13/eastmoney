# 东方财富研报工具

## 项目概述
基于东方财富API的研报查询和下载命令行工具 + 跨平台桌面GUI。

## 文件结构
- `eastmoney.py` - 主程序入口（CLI）
- `cli.py` - 命令行参数解析
- `report_client.py` - API客户端
- `utils.py` - 工具函数（已有）
- `industry.json` - 行业代码数据
- `report` - Unix/Linux入口脚本
- `report.bat` - Windows入口脚本

## GUI版本（新增）
- `gui/main.py` - GUI主入口
- `gui/main_window.py` - 主窗口（整合所有功能）
- `gui/utils/download_manager.py` - 多线程下载管理器
- `gui.bat` - Windows启动脚本

### GUI功能
- 行业分类树状列表
- 多类型研报查询（行业/个股/策略/宏观/晨报）
- 研报表格展示
- 单选/批量下载PDF
- 下载历史记录
- 多线程下载

## 使用方法（推荐使用 report 命令）

### Windows
```bash
report list
report list -s 游戏
report query -t industry -i 1046 -s 20
report download -t industry -i 1046 -s 5 -o ./reports
```

### macOS / Linux
```bash
chmod +x report
./report list
./report query -t strategy -s 5
./report download -t industry -i 1046 -o ./reports
```

## 参数说明
- `-t, --type`: 研报类型 (industry/stock/strategy/macro/morning)
- `-i, --industry`: 行业代码
- `-c, --code`: 股票代码
- `-p, --page`: 页码
- `-s, --pagesize`: 每页数量
- `-o, --output`: 输出目录
- `--begin`: 开始日期
- `--end`: 结束日期

## 注意
- 策略报告、宏观研究、个股研报需要进一步研究API参数（目前行业研报已可用）

## 问题修复记录

### 2025-03-28: PDF下载1KB问题
**问题**: PDF下载后只有1KB，实际上是东方财富反爬虫返回的JavaScript验证代码
**原因**: requests库请求被EO_Bot反爬虫识别并拦截
**解决方案**: 修改report_client.py中的download_pdf方法，使用curl代替requests下载PDF
**验证**: 下载的PDF文件大小426KB，文件头为%PDF，为有效PDF文件

### 2025-03-28: 策略报告PDF下载404问题
**问题**: 策略报告PDF下载失败，返回404错误
**原因**: 策略/宏观/晨报API返回的是 `encodeUrl` 字段而非 `infoCode`，且URL模板不同
- 行业: `https://data.eastmoney.com/report/zw_industry.jshtml?infocode=xxx`
- 策略: `https://data.eastmoney.com/report/zw_strategy.jshtml?encodeUrl=xxx`
**解决方案**: 
1. 添加 REPORT_URL_TEMPLATES 字典存储各类型URL模板
2. 修改 parse_reports 方法，根据报告类型选择正确的URL字段和模板
**验证**: 下载成功，PDF文件大小268KB

### 2025-03-28: 鼠标悬停文字看不清+下载按钮显示不全
**问题**:
1. 鼠标放表格行上时文字变白看不清
2. 下载按钮显示不全
**解决方案**:
1. 修改表格hover样式，添加明确的文字颜色 #1E293B
2. 增加下载按钮宽度从80到100，操作列宽从90到110
**验证**: 已修复

### 2026-03-28: 待下载功能（类似购物车）
**功能**: 新增"待下载"功能，允许用户勾选研报后批量下载
**实现**:
1. 将原 cart 变量重命名为 download_list
2. 实现 on_item_check_changed 方法监听复选框变化
3. 在状态栏添加"📥 待下载(N)"标签
4. 点击标签弹出待下载列表面板
5. 支持清空待下载和批量下载
**使用方式**:
1. 在表格中勾选复选框添加到待下载列表
2. 点击状态栏"待下载"标签查看列表
3. 可选择"清空"或"批量下载"
