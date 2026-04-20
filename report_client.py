#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
东方财富研报API客户端
封装各类研报的API调用逻辑
"""

import json
import os
import re
import time
from datetime import datetime

import lxml.html
import requests


class ReportType:
    """研报类型常量"""
    INDUSTRY = 'industry'      # 行业研报
    STOCK = 'stock'            # 个股研报
    STRATEGY = 'strategy'     # 策略报告
    MACRO = 'macro'           # 宏观研究
    MORNING = 'morning'       # 券商晨报 (综合)


# 研报类型对应的qType值 (根据API文档)
# /jg 接口: 宏观(qType=3), 策略(qType=2), 晨报(qType=4)
# /list 接口: 行业(qType=1)
REPORT_TYPE_QTYPE = {
    ReportType.INDUSTRY: '1',  # 行业研报 (qType=1, /list)
    ReportType.STOCK: '1',      # 个股研报 (qType=1, /list2 POST)
    ReportType.STRATEGY: '2',   # 策略报告 (qType=2, /jg)
    ReportType.MACRO: '3',      # 宏观研究 (qType=3, /jg)
    ReportType.MORNING: '4',   # 券商晨报 (qType=4, /jg)
}

# column字段前缀与研报类型的对应关系 (使用前9位精确匹配)
# 002001001xxx - 宏观研究
# 002001002xxx - 策略报告 (含市场点评)
# 002003001xxx - 券商晨报
REPORT_TYPE_COLUMN_PREFIX = {
    ReportType.MACRO: '002001001',      # 宏观研究
    ReportType.STRATEGY: '002001002',   # 策略报告
    ReportType.MORNING: '002003001',   # 券商晨报 (更精确匹配)
}


class EastMoneyReportClient:
    """东方财富研报API客户端"""
    
    # 行业研报和个股研报用 /list 接口
    LIST_API_URL = 'https://reportapi.eastmoney.com/report/list'
    # 宏观、策略、晨报用 /jg 接口
    JG_API_URL = 'https://reportapi.eastmoney.com/report/jg'
    # 个股研报用 /list2 接口 (POST)
    LIST2_API_URL = 'https://reportapi.eastmoney.com/report/list2'
    
    REPORT_INFO_URL = 'https://data.eastmoney.com/report/zw_industry.jshtml?infocode='
    INDUSTRY_API_URL = 'https://datacenter.eastmoney.com/api/data/v1/get'
    
    # 不同类型研报的URL模板 (encodeUrl方式)
    # 注意：晨报(MORNING)与宏观研究(MACRO)共用同一个详情页模板
    REPORT_URL_TEMPLATES = {
        ReportType.INDUSTRY: 'https://data.eastmoney.com/report/zw_industry.jshtml?encodeUrl=',
        ReportType.STRATEGY: 'https://data.eastmoney.com/report/zw_strategy.jshtml?encodeUrl=',
        ReportType.MACRO: 'https://data.eastmoney.com/report/zw_macresearch.jshtml?encodeUrl=',
        ReportType.MORNING: 'https://data.eastmoney.com/report/zw_macresearch.jshtml?encodeUrl=',  # 晨报详情页与宏观共用
    }
    
    def __init__(self, output_dir='./reports'):
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.industry_data = self._load_industry_data()
    
    def _load_industry_data(self):
        """加载行业数据"""
        try:
            with open('industry.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def update_industry_data(self):
        """从东方财富API更新行业数据"""
        print('正在从东方财富获取最新行业列表...')
        
        # 尝试从行业研报API获取完整行业列表
        try:
            # 使用较大的时间范围和pageSize来获取更多行业数据
            params = {
                'pageSize': 500,
                'pageNo': 1,
                'beginTime': '2020-01-01',  # 扩大时间范围
                'endTime': '2026-12-31',
                'qType': '1',
                'industry': '*',
                'industryCode': '*'
            }
            response = self.session.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if data.get('data'):
                # 从返回数据中提取行业列表
                industries = {}
                for item in data.get('data', []):
                    ind_name = item.get('industryName', '')
                    ind_code = item.get('industryCode', '')
                    if ind_name and ind_code and ind_code not in industries:
                        industries[ind_code] = {
                            'industry_name': ind_name,
                            'industry_code': ind_code,
                            'page_size': 100
                        }
                
                if industries:
                    industry_list = list(industries.values())
                    # 按行业代码排序
                    industry_list.sort(key=lambda x: x['industry_code'])
                    # 保存到文件
                    with open('industry.json', 'w', encoding='utf-8') as f:
                        json.dump(industry_list, f, ensure_ascii=False, indent=2)
                    
                    self.industry_data = industry_list
                    print(f'成功更新 {len(industry_list)} 个行业')
                    return True
        except Exception as e:
            print(f'API方式获取失败: {e}')
        
        print('无法在线更新，将使用内置的行业分类')
        return False
    
    def get_industry_list(self):
        """获取行业列表"""
        return self.industry_data
    
    def search_industry(self, keyword):
        """搜索行业"""
        if not keyword:
            return self.industry_data
        return [i for i in self.industry_data if keyword in i.get('industry_name', '')]
    
    def get_industry_name(self, industry_code):
        """根据行业代码获取行业名称"""
        for item in self.industry_data:
            if item.get('industry_code') == str(industry_code):
                return item.get('industry_name')
        return None
    
    def build_url(self, report_type=ReportType.INDUSTRY, industry_code=None, stock_code=None,
                  page_no=1, page_size=20, begin_time=None, end_time=None):
        """构建API请求URL
        
        根据 report_type 选择正确的 API 接口:
        - 行业研报: /list
        - 策略/宏观/晨报: /jg
        - 个股研报: /list2 (POST)
        """
        # 设置默认时间
        if not begin_time:
            begin_time = (datetime.now().replace(day=1)).strftime('%Y-%m-%d')
        if not end_time:
            end_time = datetime.now().strftime('%Y-%m-%d')
        
        # 获取qType
        q_type = REPORT_TYPE_QTYPE.get(report_type, '1')
        
        # 根据研报类型选择正确的API接口
        if report_type == ReportType.STOCK:
            # 个股研报使用 /list2 接口 (POST)
            base_url = self.LIST2_API_URL
        elif report_type == ReportType.INDUSTRY:
            # 行业研报使用 /list 接口
            base_url = self.LIST_API_URL
        else:
            # 策略、宏观、晨报使用 /jg 接口
            base_url = self.JG_API_URL
        
        # 构建参数
        params = {
            'pageSize': page_size,
            'pageNo': page_no,
            'beginTime': begin_time,
            'endTime': end_time,
            'qType': q_type,
            'fields': '',
            'industry': '*',
            'rating': '*',
            'ratingChange': '*',
            'orgCode': '',
            'rcode': '',
        }
        
        # 根据类型添加不同参数
        if report_type == ReportType.INDUSTRY and industry_code:
            params['industryCode'] = industry_code
        elif report_type == ReportType.STOCK and stock_code:
            params['code'] = stock_code  # 个股用 code 参数
        
        # 构建URL
        url = base_url + '?' + '&'.join([f'{k}={v}' for k, v in params.items()])
        return url
    
    def fetch_reports(self, report_type=ReportType.INDUSTRY, industry_code=None, stock_code=None,
                      page_no=1, page_size=20, begin_time=None, end_time=None):
        """获取研报列表
        
        根据 report_type 使用 GET 或 POST 请求:
        - 个股研报: POST 到 /list2
        - 其他: GET 请求
        """
        url = self.build_url(
            report_type=report_type,
            industry_code=industry_code,
            stock_code=stock_code,
            page_no=page_no,
            page_size=page_size,
            begin_time=begin_time,
            end_time=end_time
        )
        
        print(f'请求URL: {url}')
        
        try:
            # 个股研报使用 POST 请求
            if report_type == ReportType.STOCK:
                # 从URL中提取参数构建POST body
                from urllib.parse import urlparse, parse_qs
                parsed = urlparse(url)
                params = parse_qs(parsed.query)
                
                # 构建POST请求体
                post_data = {
                    'pageSize': page_size,
                    'pageNo': page_no,
                    'p': page_no,
                    'pageNum': page_no,
                    'pageNumber': page_no,
                    'beginTime': begin_time or (datetime.now().replace(day=1)).strftime('%Y-%m-%d'),
                    'endTime': end_time or datetime.now().strftime('%Y-%m-%d'),
                    'code': stock_code if stock_code else '*',
                    'industryCode': '*',
                    'rating': None,
                    'ratingChange': None,
                    'orgCode': None,
                    'rcode': ''
                }
                
                response = self.session.post(
                    self.LIST2_API_URL,
                    json=post_data,
                    headers={'Content-Type': 'application/json'}
                )
            else:
                response = self.session.get(url)
            
            response.raise_for_status()
            
            # 解析响应 - 可能是JSON或JSONP
            text = response.text
            if not text:
                print('响应为空')
                return None
            
            # 尝试直接解析JSON
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                pass
            
            # 尝试解析JSONP格式
            match = re.search(r'\((.+)\)', text, re.DOTALL)
            if match:
                json_str = match.group(1)
                data = json.loads(json_str)
                return data
            
            # 如果都不行，返回原始文本
            print(f'响应内容: {text[:500]}...' if len(text) > 500 else f'响应内容: {text}')
            return None
                
        except requests.RequestException as e:
            print(f'请求失败: {e}')
            return None
        except json.JSONDecodeError as e:
            print(f'JSON解析失败: {e}')
            print(f'响应内容: {text[:500]}...' if len(text) > 500 else f'响应内容: {text}')
            return None
    
    def parse_reports(self, data, report_type=None):
        """解析研报数据
        
        Args:
            data: API返回的原始数据
            report_type: 研报类型，用于过滤
        """
        if not data or not data.get('data'):
            return []
        
        reports = []
        for item in data['data']:
            # 策略/宏观/晨报使用 encodeUrl 字段
            # 行业/个股研报使用 infoCode 字段
            encode_url = item.get('encodeUrl', '')
            info_code = item.get('infoCode', '')
            
            # 根据报告类型构建URL
            if encode_url:
                # 策略、宏观、晨报使用 encodeUrl
                url_template = self.REPORT_URL_TEMPLATES.get(report_type, '')
                if url_template:
                    report_url = url_template + encode_url
                else:
                    report_url = self.REPORT_INFO_URL + info_code
            else:
                # 行业研报使用 infoCode
                report_url = self.REPORT_INFO_URL + info_code
            
            report = {
                'title': item.get('title', ''),
                'org_name': item.get('orgSName', ''),       # 机构名称
                'publish_date': item.get('publishDate', ''), # 发布日期
                'industry_name': item.get('industryName', ''),  # 行业
                'stock_name': item.get('stockName', ''),     # 股票名称
                'stock_code': item.get('stockCode', ''),     # 股票代码
                'info_code': info_code or encode_url,        # 兼容两种ID
                'encode_url': encode_url,                     # 策略/宏观/晨报专用
                'report_type': item.get('reportType', ''),   # 研报类型
                'rating_name': item.get('ratingName', ''),   # 评级
                'column': item.get('column', ''),            # 栏目标识
                'url': report_url
            }
            reports.append(report)
        
        return reports
    
    def display_reports(self, reports, page_no=1):
        """格式化显示研报列表"""
        if not reports:
            print('未找到研报')
            return
        
        print(f'\n{"="*100}')
        print(f'第 {page_no} 页，共 {len(reports)} 条研报')
        print(f'{"="*100}')
        
        print(f'{"序号":<4} {"研报标题":<45} {"机构":<15} {"日期":<12} {"股票/行业":<15}')
        print('-'*100)
        
        for idx, report in enumerate(reports, 1):
            title = report['title'][:42] + '...' if len(report['title']) > 45 else report['title']
            org = report['org_name'][:13] + '..' if len(report['org_name']) > 15 else report['org_name']
            date = report['publish_date'][:10]
            # 优先显示股票名称，否则显示行业
            stock_info = report['stock_name'] or report['industry_name']
            stock_info = stock_info[:13] + '..' if len(stock_info) > 15 else stock_info
            
            print(f'{idx:<4} {title:<45} {org:<15} {date:<12} {stock_info:<15}')
        
        print(f'{"="*100}\n')
    
    def save_reports_to_csv(self, reports, filename):
        """保存研报到CSV文件"""
        import csv
        
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
            fieldnames = ['title', 'org_name', 'publish_date', 'stock_name', 'stock_code', 
                         'industry_name', 'rating_name', 'info_code', 'url']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for report in reports:
                writer.writerow({k: report.get(k, '') for k in fieldnames})
        
        print(f'已保存到: {filename}')
    
    def get_pdf_url(self, report_url, info_code):
        """从研报页面获取PDF下载链接"""
        try:
            response = self.session.get(report_url, timeout=10)
            response.raise_for_status()
            
            selector = lxml.html.fromstring(response.content)
            pdf_links = selector.xpath('//span[@class="to-link"]/a[@class="pdf-link"]/@href')
            
            if pdf_links:
                return pdf_links[0]
            
            return None
            
        except requests.RequestException as e:
            print(f'获取PDF链接失败: {e}')
            return None
    
    def download_pdf(self, pdf_url, save_path):
        """下载PDF文件 - 使用curl绕过反爬虫"""
        import subprocess
        
        os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)
        
        try:
            # 使用curl下载，添加User-Agent伪装
            cmd = [
                'curl', '-L', '-o', save_path, '-A', 
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                pdf_url
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # 检查下载的文件是否有效（不是HTML或JS）
                with open(save_path, 'rb') as f:
                    header = f.read(4)
                if header == b'%PDF':
                    return True
                else:
                    print(f'下载的文件不是PDF，可能是反爬虫拦截')
                    return False
            else:
                print(f'下载失败: {result.stderr}')
                return False
                
        except Exception as e:
            print(f'下载失败: {e}')
            return False
    
    def download_reports(self, reports, output_dir, report_type='industry'):
        """批量下载研报PDF"""
        os.makedirs(output_dir, exist_ok=True)
        
        # 按类型创建子目录
        type_dir = os.path.join(output_dir, report_type)
        os.makedirs(type_dir, exist_ok=True)
        
        success_count = 0
        fail_count = 0
        
        for report in reports:
            title = report['title']
            # 清理文件名中的非法字符
            safe_title = re.sub(r'[\\/:*?"<>|]', '', title)
            safe_title = safe_title[:100]  # 限制文件名长度
            
            pdf_path = os.path.join(type_dir, f'{safe_title}.pdf')
            
            print(f'正在下载: {title}...')
            
            # 获取PDF链接
            pdf_url = self.get_pdf_url(report['url'], report.get('info_code'))
            if not pdf_url:
                print(f'  获取PDF链接失败')
                fail_count += 1
                continue
            
            # 下载PDF
            if self.download_pdf(pdf_url, pdf_path):
                print(f'  下载成功: {pdf_path}')
                success_count += 1
            else:
                fail_count += 1
        
        print(f'\n下载完成: 成功 {success_count}, 失败 {fail_count}')
        return success_count, fail_count
    
    def get_total_pages(self, data):
        """从响应数据中获取总页数"""
        if not data:
            return 0
        # API返回的总数量
        return data.get('total', 0)
