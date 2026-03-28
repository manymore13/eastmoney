#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
东方财富研报命令行工具
支持查询和下载行业研报、个股研报、策略报告、宏观研究、券商晨报
"""

import argparse
import sys
from datetime import datetime


def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description='''
=======================================================================
              东方财富研报命令行工具 v1.0
               查询和下载研报PDF的利器
=======================================================================
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
=======================================================================
快速开始

  # 1. 查看所有行业
  report l
  
  # 2. 搜索特定行业
  report l -s 游戏
  
  # 3. 查询某行业研报 (如游戏行业代码1046)
  report q -i 1046
  
  # 4. 下载研报PDF
  report d -i 1046 -o ./reports
  
  # 5. 更新行业列表
  report u

=======================================================================
命令简写

  query    -> q    (查询研报)
  download -> d    (下载PDF)
  list     -> l    (查看行业)
  update   -> u    (更新行业)

=======================================================================
研报类型

  类型          用法                          说明
  ─────────────────────────────────────────────────────────────────────
  行业研报      report q -i 1046             分析某个行业的报告（如游戏、医疗）
  策略报告      report q -t strategy         市场分析、投资策略类报告
  宏观研究      report q -t macro           宏观经济形势研究
  券商晨报      report q -t morning         每天早上的简短资讯
  个股研报      report q -t stock -c 600519  分析某只股票的报告（如茅台600519）

提示: 不指定 -t 时默认查询行业研报

=======================================================================
常见用法

  【行业研报】
    report q -i 1046                    # 查询游戏行业研报
    report q -i 1046 -s 10              # 查询10条

  【个股研报】
    report q -t stock -c 600519         # 查询茅台研报
    report q -t stock -c 000001        # 查询平安银行研报

  【策略报告】
    report q -t strategy                # 查询策略报告

  【宏观研究】
    report q -t macro                   # 查询宏观研究报告

  【券商晨报】
    report q -t morning                 # 查询券商晨报

  【下载研报】
    report d -i 1046 -o ./reports       # 下载行业研报
    report d -t stock -c 600519 -o ./mt # 下载茅台研报

  【行业管理】
    report l                            # 查看所有行业
    report l -s 银行                    # 搜索"银行"相关行业
    report u                           # 从官网更新行业列表

=======================================================================
链接

  行业研报: https://data.eastmoney.com/report/industry.jshtml
  个股研报: https://data.eastmoney.com/report/stock.jshtml
        '''
    )
    
    # 添加子命令
    # 设置 prog 为 report.py 以便显示正确的命令名
    subparsers = parser.add_subparsers(dest='command', help='可用命令 (输入 help 查看详情)', prog='report')

    # ==================== query 命令 ====================
    parser_query = subparsers.add_parser(
        'query', 
        aliases=['q'], 
        help='查询研报列表',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
用法示例

  report q -i 1046                    # 查询游戏行业研报
  report q -i 1046 -p 2 -s 20        # 查询第2页，每页20条
  report q -t stock -c 600519         # 查询茅台个股研报
  report q -i 1046 --begin 2025-01-01 # 按日期筛选
  report q -i 1046 --save-csv         # 查询并保存CSV文件

注意: 行业代码用 -i 参数，股票代码用 -c 参数
        '''
    )
    parser_query.add_argument(
        '-t', '--type', 
        type=str, 
        choices=['industry', 'stock', 'strategy', 'macro', 'morning'],
        default='industry',
        help='研报类型: industry(行业) | stock(个股) | strategy(策略) | macro(宏观) | morning(晨报) [默认: industry]'
    )
    parser_query.add_argument(
        '-i', '--industry',
        type=str,
        help='行业代码 (如 1046 = 游戏行业)'
    )
    parser_query.add_argument(
        '-c', '--code',
        type=str,
        help='股票代码 (如 600519 = 贵州茅台)'
    )
    parser_query.add_argument(
        '-p', '--page',
        type=int,
        default=1,
        help='页码 [默认: 1]'
    )
    parser_query.add_argument(
        '-s', '--pagesize',
        type=int,
        default=20,
        help='每页数量 [默认: 20]'
    )
    parser_query.add_argument(
        '--begin',
        type=str,
        help='开始日期 (格式: YYYY-MM-DD)'
    )
    parser_query.add_argument(
        '--end',
        type=str,
        help='结束日期 (格式: YYYY-MM-DD)'
    )
    parser_query.add_argument(
        '-o', '--output',
        type=str,
        help='CSV输出目录'
    )
    parser_query.add_argument(
        '--save-csv',
        action='store_true',
        help='将结果保存为CSV文件'
    )
    
    # ==================== download 命令 ====================
    parser_download = subparsers.add_parser(
        'download', 
        aliases=['d'], 
        help='下载研报PDF',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
用法示例

  report d -i 1046 -o ./reports      # 下载游戏行业研报
  report d -i 1046 -p 1 -s 5         # 下载第1页的5篇
  report d -c 600519 -o ./reports     # 下载茅台个股研报
  report d -i 1046 --all              # 下载该行业所有研报

注意: PDF会保存到指定目录的子目录中 (如: ./reports/industry/)
        '''
    )
    parser_download.add_argument(
        '-t', '--type',
        type=str,
        choices=['industry', 'stock', 'strategy', 'macro', 'morning'],
        default='industry',
        help='研报类型 [默认: industry]'
    )
    parser_download.add_argument(
        '-i', '--industry',
        type=str,
        help='行业代码 (如 1046 = 游戏行业)'
    )
    parser_download.add_argument(
        '-c', '--code',
        type=str,
        help='股票代码 (如 600519 = 贵州茅台)'
    )
    parser_download.add_argument(
        '-p', '--page',
        type=int,
        default=1,
        help='下载第几页 [默认: 1]'
    )
    parser_download.add_argument(
        '-s', '--pagesize',
        type=int,
        default=20,
        help='每页数量 [默认: 20]'
    )
    parser_download.add_argument(
        '-o', '--output',
        type=str,
        default='./reports',
        help='输出目录 [默认: ./reports]'
    )
    parser_download.add_argument(
        '--begin',
        type=str,
        help='开始日期 (格式: YYYY-MM-DD)'
    )
    parser_download.add_argument(
        '--end',
        type=str,
        help='结束日期 (格式: YYYY-MM-DD)'
    )
    parser_download.add_argument(
        '--all',
        action='store_true',
        help='下载该类型所有行业的研报'
    )
    
    # ==================== list 命令 ====================
    parser_list = subparsers.add_parser(
        'list', 
        aliases=['l'], 
        help='列出所有行业',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
用法示例

  report l                    # 查看所有行业
  report l -s 游戏            # 搜索"游戏"行业
  report l -s 银行            # 搜索"银行"相关行业

提示: 先用 list 查看行业代码，再用于 query 或 download
        '''
    )
    parser_list.add_argument(
        '-s', '--search',
        type=str,
        help='按关键词搜索行业名称'
    )
    
    # ==================== update 命令 ====================
    parser_update = subparsers.add_parser(
        'update', 
        aliases=['u'], 
        help='更新行业列表',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
用法示例

  report u                    # 从东方财富官网更新行业列表

提示: 当行业列表有更新时，运行此命令同步最新数据
        '''
    )
    
    return parser


def parse_args(args=None):
    """解析命令行参数"""
    parser = create_parser()
    parsed = parser.parse_args(args)
    
    # 验证参数组合
    if parsed.command == 'query':
        if parsed.type == 'industry' and not parsed.industry:
            parser.error('错误: 行业研报需要指定行业代码 (-i 参数)\n   用法: py -3 -m eastmoney q -i 1046')
        if parsed.type == 'stock' and not parsed.code:
            parser.error('错误: 个股研报需要指定股票代码 (-c 参数)\n   用法: py -3 -m eastmoney q -c 600519')
        if parsed.type in ['strategy', 'macro', 'morning'] and parsed.industry:
            parser.error(f'错误: {parsed.type} 类型不需要指定行业代码')
            
    elif parsed.command == 'download':
        if parsed.type == 'industry' and not parsed.industry and not parsed.all:
            parser.error('错误: 下载行业研报需要指定行业代码 (-i) 或使用 --all 参数')
        if parsed.type == 'stock' and not parsed.code:
            parser.error('错误: 下载个股研报需要指定股票代码 (-c 参数)\n   用法: py -3 -m eastmoney d -c 600519 -o ./reports')
    
    return parsed


def validate_date(date_str, parser):
    """验证日期格式"""
    if not date_str:
        return None
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return date_str
    except ValueError:
        parser.error(f'错误: 日期格式错误 {date_str}，请使用 YYYY-MM-DD 格式')


if __name__ == '__main__':
    args = parse_args()
    print(args)
