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
    MORNING = 'morning'       # 券商晨报


# 研报类型对应的qType值
# 注意：东方财富API可能需要不同的接口来获取不同类型的研报
# 以下参数基于API文档推测，需要进一步验证
REPORT_TYPE_QTYPE = {
    ReportType.INDUSTRY: '1',  # 行业研报
    ReportType.STOCK: '3',     # 个股研报 (待验证)
    ReportType.STRATEGY: '3',  # 策略报告 (待验证)
    ReportType.MACRO: '4',     # 宏观研究 (待验证)
    ReportType.MORNING: '2',   # 券商晨报 (待验证)
}


class EastMoneyReportClient:
    """东方财富研报API客户端"""
    
    BASE_URL = 'https://reportapi.eastmoney.com/report/list'
    REPORT_INFO_URL = 'https://data.eastmoney.com/report/zw_industry.jshtml?infocode='
    
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
        """构建API请求URL"""
        # 设置默认时间
        if not begin_time:
            begin_time = (datetime.now().replace(day=1)).strftime('%Y-%m-%d')
        if not end_time:
            end_time = datetime.now().strftime('%Y-%m-%d')
        
        # 获取qType
        q_type = REPORT_TYPE_QTYPE.get(report_type, '1')
        
        # 构建参数 - 移除cb参数，直接返回JSON
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
            params['stockCode'] = stock_code
        
        # 构建URL
        url = self.BASE_URL + '?' + '&'.join([f'{k}={v}' for k, v in params.items()])
        return url
    
    def fetch_reports(self, report_type=ReportType.INDUSTRY, industry_code=None, stock_code=None,
                      page_no=1, page_size=20, begin_time=None, end_time=None):
        """获取研报列表"""
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
    
    def parse_reports(self, data):
        """解析研报数据"""
        if not data or not data.get('data'):
            return []
        
        reports = []
        for item in data['data']:
            report = {
                'title': item.get('title', ''),
                'org_name': item.get('orgSName', ''),       # 机构名称
                'publish_date': item.get('publishDate', ''), # 发布日期
                'industry_name': item.get('industryName', ''),  # 行业
                'stock_name': item.get('stockName', ''),     # 股票名称
                'stock_code': item.get('stockCode', ''),     # 股票代码
                'info_code': item.get('infoCode', ''),       # 研报ID
                'report_type': item.get('reportType', ''),   # 研报类型
                'rating_name': item.get('ratingName', ''),   # 评级
                'url': self.REPORT_INFO_URL + item.get('infoCode', '')
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
