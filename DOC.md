# 东方财富研报 MCP Server

基于东方财富数据接口的研报查询和下载工具，支持通过 MCP 协议与大模型集成。

## 功能特性

- **行业研报查询**: 查询各行业的研究报告
- **个股研报查询**: 查询特定股票的研究报告
- **策略报告**: 获取市场策略分析报告
- **宏观研究**: 获取宏观经济研究报告
- **券商晨报**: 获取券商晨会报告
- **PDF 下载**: 支持批量下载研报 PDF 文件

## 支持的研报类型

| 类型 | 说明 | 参数 |
|------|------|------|
| `industry` | 行业研报 | 需指定行业代码 |
| `stock` | 个股研报 | 需指定股票代码 |
| `strategy` | 策略报告 | 无需额外参数 |
| `macro` | 宏观研究 | 无需额外参数 |
| `morning` | 券商晨报 | 无需额外参数 |

## 使用示例

### 查询行业列表

```
请列出所有可用的行业分类
```

### 查询游戏行业研报

```
查询游戏行业的研究报告，显示前10条
```

### 下载策略报告

```
下载最新的5份策略报告到本地
```

## 工具列表

### list_industries

列出所有可用的行业分类，用于查询研报前选择行业代码。

**参数**:
- `search` (可选): 搜索关键词过滤行业名称

### query_reports

查询研报列表。

**参数**:
- `type`: 研报类型 (industry/stock/strategy/macro/morning)
- `industry`: 行业代码 (查询行业研报时使用)
- `stock_code`: 股票代码 (查询个股研报时使用)
- `page`: 页码，默认 1
- `pagesize`: 每页数量，默认 10
- `begin`: 开始日期，格式 YYYY-MM-DD
- `end`: 结束日期，格式 YYYY-MM-DD

### download_reports

下载研报 PDF 文件。

**参数**:
- `type`: 研报类型
- `industry`: 行业代码
- `stock_code`: 股票代码
- `page`: 页码
- `pagesize`: 每页数量
- `output`: 输出目录

### get_industry_code

根据关键词搜索行业代码。

**参数**:
- `keyword`: 行业名称关键词

## 数据来源

数据来源于东方财富网 (data.eastmoney.com)，仅供学习研究使用。

## 远程 MCP

本项目支持[一键部署到腾讯云开发平台](https://docs.cloudbase.net/ai/mcp/develop/host-mcp)，提供远程 Streamable HTTP 访问。

[☁️ 前往云开发平台部署 MCP Server](https://tcb.cloud.tencent.com/dev#/ai?tab=mcp)

## 开源协议

MIT License
