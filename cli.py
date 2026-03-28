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
        description='东方财富研报命令行工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例用法:
  # 查询行业研报
  python -m eastmoney query --type industry --industry 1046 --page 1 --pagesize 20
  
  # 查询个股研报
  python -m eastmoney query --type stock --code 600519 --page 1
  
  # 查询策略报告
  python -m eastmoney query --type strategy --page 1
  
  # 查询宏观研究
  python -m eastmoney query --type macro --page 1
  
  # 查询券商晨报
  python -m eastmoney query --type morning --page 1
  
  # 下载研报
  python -m eastmoney download --type industry --industry 1046 --output ./reports
  
  # 列出所有行业
  python -m eastmoney list
        '''
    )
    
    # 添加子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # ==================== query 命令 ====================
    parser_query = subparsers.add_parser('query', help='查询研报')
    parser_query.add_argument(
        '-t', '--type', 
        type=str, 
        choices=['industry', 'stock', 'strategy', 'macro', 'morning'],
        default='industry',
        help='研报类型: industry(行业研报), stock(个股研报), strategy(策略报告), macro(宏观研究), morning(券商晨报)'
    )
    parser_query.add_argument(
        '-i', '--industry',
        type=str,
        help='行业代码，如 1046 (游戏行业)'
    )
    parser_query.add_argument(
        '-c', '--code',
        type=str,
        help='股票代码，如 600519 (贵州茅台)'
    )
    parser_query.add_argument(
        '-p', '--page',
        type=int,
        default=1,
        help='页码 (默认: 1)'
    )
    parser_query.add_argument(
        '-s', '--pagesize',
        type=int,
        default=20,
        help='每页数量 (默认: 20)'
    )
    parser_query.add_argument(
        '--begin',
        type=str,
        help='开始日期，格式: YYYY-MM-DD'
    )
    parser_query.add_argument(
        '--end',
        type=str,
        help='结束日期，格式: YYYY-MM-DD'
    )
    parser_query.add_argument(
        '-o', '--output',
        type=str,
        help='输出目录'
    )
    parser_query.add_argument(
        '--save-csv',
        action='store_true',
        help='保存为CSV文件'
    )
    
    # ==================== download 命令 ====================
    parser_download = subparsers.add_parser('download', help='下载研报PDF')
    parser_download.add_argument(
        '-t', '--type',
        type=str,
        choices=['industry', 'stock', 'strategy', 'macro', 'morning'],
        default='industry',
        help='研报类型'
    )
    parser_download.add_argument(
        '-i', '--industry',
        type=str,
        help='行业代码'
    )
    parser_download.add_argument(
        '-c', '--code',
        type=str,
        help='股票代码'
    )
    parser_download.add_argument(
        '-p', '--page',
        type=int,
        default=1,
        help='下载第几页的研报 (默认: 1)'
    )
    parser_download.add_argument(
        '-s', '--pagesize',
        type=int,
        default=20,
        help='每页数量 (默认: 20)'
    )
    parser_download.add_argument(
        '-o', '--output',
        type=str,
        default='./reports',
        help='输出目录 (默认: ./reports)'
    )
    parser_download.add_argument(
        '--begin',
        type=str,
        help='开始日期，格式: YYYY-MM-DD'
    )
    parser_download.add_argument(
        '--end',
        type=str,
        help='结束日期，格式: YYYY-MM-DD'
    )
    parser_download.add_argument(
        '--all',
        action='store_true',
        help='下载所有行业的研报'
    )
    
    # ==================== list 命令 ====================
    parser_list = subparsers.add_parser('list', help='列出所有行业')
    parser_list.add_argument(
        '-s', '--search',
        type=str,
        help='搜索行业名称'
    )
    
    return parser


def parse_args(args=None):
    """解析命令行参数"""
    parser = create_parser()
    parsed = parser.parse_args(args)
    
    # 验证参数组合
    if parsed.command == 'query':
        if parsed.type == 'industry' and not parsed.industry:
            parser.error('行业研报需要指定 --industry 参数')
        if parsed.type == 'stock' and not parsed.code:
            parser.error('个股研报需要指定 --code 参数')
        if parsed.type in ['strategy', 'macro', 'morning'] and parsed.industry:
            parser.error(f'{parsed.type} 类型不需要 --industry 参数')
            
    elif parsed.command == 'download':
        if parsed.type == 'industry' and not parsed.industry and not parsed.all:
            parser.error('下载行业研报需要指定 --industry 或 --all 参数')
        if parsed.type == 'stock' and not parsed.code:
            parser.error('下载个股研报需要指定 --code 参数')
    
    return parsed


def validate_date(date_str, parser):
    """验证日期格式"""
    if not date_str:
        return None
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return date_str
    except ValueError:
        parser.error(f'日期格式错误: {date_str}，请使用 YYYY-MM-DD 格式')


if __name__ == '__main__':
    args = parse_args()
    print(args)
