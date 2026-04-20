#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
东方财富研报 MCP 服务器 (FastMCP 版本)
让大模型可以通过 MCP 协议调用研报查询和下载功能
"""

import os
import json
from typing import Optional, Literal
from fastmcp import FastMCP

# 导入现有的客户端
import report_client

# 创建 FastMCP 实例
mcp = FastMCP(
    name="eastmoney-reports",
    version="2.0.0"
)

# 初始化客户端
client = report_client.EastMoneyReportClient()


@mcp.tool()
def list_industries(search: Optional[str] = None) -> str:
    """列出所有可用的行业分类，用于查询研报前选择行业代码

    Args:
        search: 可选，搜索关键词过滤行业名称

    Returns:
        行业列表，包含行业代码和名称
    """
    industries = client.search_industry(search or "")

    if not industries:
        return "未找到匹配的行业"

    result = ["行业代码\t行业名称", "-" * 40]
    for ind in industries:
        result.append(f"{ind['industry_code']}\t{ind['industry_name']}")

    result.append(f"\n共 {len(industries)} 个行业")
    return "\n".join(result)


@mcp.tool()
def query_reports(
    type: Literal["industry", "stock", "strategy", "macro", "morning"] = "industry",
    industry: Optional[str] = None,
    stock_code: Optional[str] = None,
    page: int = 1,
    pagesize: int = 10,
    begin: Optional[str] = None,
    end: Optional[str] = None
) -> str:
    """查询研报列表

    支持多种研报类型:
    - industry: 行业研报 (需要指定 industry 行业代码)
    - stock: 个股研报 (需要指定 stock_code 股票代码)
    - strategy: 策略报告
    - macro: 宏观研究
    - morning: 券商晨报

    Args:
        type: 研报类型，可选值: industry, stock, strategy, macro, morning
        industry: 行业代码，如 1046=游戏行业 (查询行业研报时使用)
        stock_code: 股票代码，如 600519=贵州茅台 (查询个股研报时使用)
        page: 页码，默认 1
        pagesize: 每页数量，默认 10
        begin: 开始日期，格式 YYYY-MM-DD
        end: 结束日期，格式 YYYY-MM-DD

    Returns:
        研报列表，包含标题、机构、日期等信息
    """
    # 映射类型
    type_map = {
        "industry": report_client.ReportType.INDUSTRY,
        "stock": report_client.ReportType.STOCK,
        "strategy": report_client.ReportType.STRATEGY,
        "macro": report_client.ReportType.MACRO,
        "morning": report_client.ReportType.MORNING
    }

    report_type = type_map.get(type, report_client.ReportType.INDUSTRY)

    # 获取研报数据
    data = client.fetch_reports(
        report_type=report_type,
        industry_code=industry,
        stock_code=stock_code,
        page_no=page,
        page_size=pagesize,
        begin_time=begin,
        end_time=end
    )

    if not data:
        return "获取研报数据失败"

    # 解析研报
    reports = client.parse_reports(data, report_type=type)

    if not reports:
        return "未找到研报"

    # 格式化输出
    result = [f"第 {page} 页，共 {len(reports)} 条研报", "=" * 80]
    result.append("标题\t机构\t日期\t股票/行业")
    result.append("-" * 80)

    for i, r in enumerate(reports, 1):
        stock_info = r.get('stock_name') or r.get('industry_name') or ''
        title = r['title'][:40] + '...' if len(r['title']) > 40 else r['title']
        result.append(f"{i}. {title}\t{r['org_name']}\t{r['publish_date'][:10]}\t{stock_info}")
        result.append(f"   链接: {r['url']}")

    return "\n".join(result)


@mcp.tool()
def download_reports(
    type: Literal["industry", "stock", "strategy", "macro", "morning"] = "industry",
    industry: Optional[str] = None,
    stock_code: Optional[str] = None,
    page: int = 1,
    pagesize: int = 5,
    output: str = "./reports"
) -> str:
    """下载研报 PDF 文件到指定目录

    Args:
        type: 研报类型，可选值: industry, stock, strategy, macro, morning
        industry: 行业代码 (查询行业研报时使用)
        stock_code: 股票代码 (查询个股研报时使用)
        page: 下载第几页，默认 1
        pagesize: 每页数量，默认 5
        output: 输出目录，默认 ./reports

    Returns:
        下载结果，包含成功和失败数量
    """
    # 映射类型
    type_map = {
        "industry": report_client.ReportType.INDUSTRY,
        "stock": report_client.ReportType.STOCK,
        "strategy": report_client.ReportType.STRATEGY,
        "macro": report_client.ReportType.MACRO,
        "morning": report_client.ReportType.MORNING
    }

    report_type = type_map.get(type, report_client.ReportType.INDUSTRY)

    # 获取研报数据
    data = client.fetch_reports(
        report_type=report_type,
        industry_code=industry,
        stock_code=stock_code,
        page_no=page,
        page_size=pagesize
    )

    if not data:
        return "获取研报数据失败"

    # 解析研报
    reports = client.parse_reports(data, report_type=type)

    if not reports:
        return "未找到研报"

    # 获取类型名称用于目录
    if type == "industry" and industry:
        type_name = client.get_industry_name(industry) or industry
    elif type == "stock" and stock_code:
        type_name = stock_code
    else:
        type_name = type

    # 下载研报
    success, fail = client.download_reports(reports, output, report_type=type_name)

    return f"下载完成: 成功 {success} 个，失败 {fail} 个\n保存目录: {os.path.join(output, type_name)}"


@mcp.tool()
def get_industry_code(keyword: str) -> str:
    """根据关键词搜索行业代码

    用于查找特定行业的代码，方便后续查询和下载研报

    Args:
        keyword: 行业名称关键词，如 "游戏"、"医药"、"新能源"

    Returns:
        匹配的行业代码和名称列表
    """
    industries = client.search_industry(keyword)

    if not industries:
        return f"未找到包含 '{keyword}' 的行业"

    result = [f"找到 {len(industries)} 个匹配的行业:", "-" * 40]
    for ind in industries:
        result.append(f"代码: {ind['industry_code']}  名称: {ind['industry_name']}")

    return "\n".join(result)


@mcp.resource("industry://list")
def get_industry_list() -> str:
    """获取完整的行业分类列表作为资源"""
    industries = client.get_industry_list()
    return json.dumps(industries, ensure_ascii=False, indent=2)


@mcp.prompt()
def query_industry_reports(industry_name: str) -> str:
    """查询指定行业的研报

    Args:
        industry_name: 行业名称，如 "游戏"、"医药"
    """
    return f"""请帮我查询 {industry_name} 行业的研究报告：
1. 先使用 get_industry_code 工具查找 "{industry_name}" 对应的行业代码
2. 然后使用 query_reports 工具查询该行业的研报
3. 总结研报的主要内容和趋势"""


@mcp.prompt()
def download_latest_reports(report_type: str = "strategy", count: int = 5) -> str:
    """下载最新研报

    Args:
        report_type: 研报类型 (strategy/macro/morning)
        count: 下载数量
    """
    return f"""请帮我下载最新的 {report_type} 类型研报：
1. 使用 download_reports 工具，type 参数设为 "{report_type}"
2. pagesize 设为 {count}
3. 完成后列出下载的文件"""


if __name__ == "__main__":
    # 运行 MCP 服务器
    mcp.run()
