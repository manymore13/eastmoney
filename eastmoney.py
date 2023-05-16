import csv
import json
import os
import re
import time
from datetime import datetime

import lxml.html
import requests

import utils


class EastMoneyReport:
    east_money_url = 'https://reportapi.eastmoney.com/report/list?cb=datatable1808538&industryCode={' \
                     'industryCode}&pageSize={pageSize}&industry=*&rating=*&ratingChange=*&beginTime={' \
                     'beginTime}&endTime={endTime}&pageNo={pageNo}&fields=&qType=1&orgCode=&rcode=&_={time}'

    report_info_url = 'https://data.eastmoney.com/report/zw_industry.jshtml?infocode='

    def __init__(self, dir_name=None):
        """
        研报助手
        :param dir_name: 研报存放的位置,目录
        """
        self.beginTime = '2021-05-14'
        self.endTime = '2023-05-14'
        self.pageSize = '50'
        self.industryCode = '1046'
        self.pageNo = '1'
        self.dir_name = dir_name
        if dir_name is None:
            self.dir_name = 'gen'
        self.industry_name_list = self.load_industry()
        self.industry_code_dic = self.load_code_dic(self.industry_name_list)

    @classmethod
    def load_code_dic(cls, industry_name_list):
        industry_code_dic = {}
        for industry in industry_name_list:
            industry_code_dic[industry['industry_code']] = industry['industry_name']
        return industry_code_dic

    @classmethod
    def load_industry(cls):
        file_name = 'industry.json'
        with open(file_name, 'r', encoding='utf-8') as f:
            return json.load(f)

    def build_url(self, industryCode=None, beginTime=None, endTime=None, pageSize=None, pageNo=None):
        if beginTime is None:
            beginTime = self.beginTime

        if beginTime is None:
            beginTime = self.beginTime

        if endTime is None:
            endTime = self.endTime

        if pageSize is None:
            pageSize = self.pageSize

        if pageNo is None:
            pageNo = self.pageNo

        if industryCode is None:
            industryCode = self.industryCode

        cur_time = int(time.time())
        report_url = self.east_money_url.format(industryCode=industryCode, pageSize=pageSize,
                                                beginTime=beginTime,
                                                endTime=endTime, pageNo=pageNo, time=cur_time)
        print('start get :' + report_url)
        return report_url

    @classmethod
    def get_report_json(cls, report_json_url):
        report_content = requests.get(report_json_url).text
        report_content = re.search('\((.+)\)', report_content).group(1)
        return report_content

    @classmethod
    def save_json(cls, dir_name, report_name, content):
        with open(os.path.join(dir_name, report_name + '.json'), 'w', encoding='utf-8') as file:
            file.write(content)

    def save_csv_and_pdf(self, dir_name, industry_name, content_json, is_download_pdf=False):
        report_list = json.loads(content_json)['data']
        report_list_data = []
        report_url_list = []
        for report in report_list:
            report_url = self.report_info_url + report['infoCode']
            report_name = report['title']
            report_data = {'研报名称': report['title'], '机构名称': report['orgSName'],
                           '发布时间': re.findall('\d+-\d+-\d+', report['publishDate'])[0],
                           '行业': report['industryName'],
                           '研报地址': report_url}
            report_list_data.append(report_data)
            report_url_list.append([report_url, report_name])

        with open(os.path.join(dir_name, industry_name + '.csv'), 'w', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['研报名称', '机构名称', '发布时间', '行业', '研报地址'])
            writer.writeheader()
            writer.writerows(report_list_data)

        if is_download_pdf is True:
            for report_url, report_name in report_url_list:
                self.__download_report_pdf(dir_name=dir_name, report_name=report_name, report_url=report_url)

    def __download_report(self, dir_name, industry_name, industryCode=None, beginTime=None, endTime=None, pageSize=None,
                          pageNo=None, is_download_pdf=False):
        utils.delete_all_files(dir_name)
        report_json_url = self.build_url(industryCode, beginTime, endTime, pageSize, pageNo)
        content_json = self.get_report_json(report_json_url)
        self.save_csv_and_pdf(dir_name, industry_name, content_json, is_download_pdf)

    @classmethod
    def __get_report_pdf_link(cls, report_url):
        """
        获取研报链接
        :param report_url:
        :return:
        """
        report_html = requests.get(report_url).content.decode('utf-8')
        report_selector = lxml.html.fromstring(report_html)
        return report_selector.xpath('//span[@class="to-link"]/a[@class="pdf-link"]/@href')[0]

    @classmethod
    def __download_report_pdf(cls, dir_name, report_name: str, report_url):
        report_name = re.sub('[/|；]', '', report_name)
        pdf_url = cls.__get_report_pdf_link(report_url)
        content = requests.get(pdf_url).content
        with open(os.path.join(dir_name, report_name + '.pdf'), 'wb') as file:
            file.write(content)

    def download_report_all(self, is_download_pdf=False):
        """
        下载所有行业研报
        :param is_download_pdf: 是否下载pdf研报,默认False不下载
        :return: None
        """

        dir_name = self.dir_name
        os.makedirs(dir_name, exist_ok=True)
        end_time = datetime.now().strftime('%Y-%m-%d')
        for industry in self.industry_name_list:
            industry_name = industry['industry_name']
            child_dir_name = os.path.join(dir_name, industry_name)
            os.makedirs(child_dir_name, exist_ok=True)
            industry_code = industry['industry_code']
            self.__download_report(dir_name=child_dir_name, industry_name=industry_name, industryCode=industry_code,
                                   is_download_pdf=is_download_pdf, endTime=end_time)

    def download_report(self, industry_code_list, pageSize=None, pageNo=None, beginTime=None, endTime=None,
                        is_download_pdf=False):
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
        self.asser_industry_code_list(industry_code_list)
        dir_name = self.dir_name
        os.makedirs(dir_name, exist_ok=True)
        if beginTime is None:
            beginTime = self.beginTime

        if endTime is None:
            endTime = datetime.now().strftime('%Y-%m-%d')
        if pageNo is None:
            pageNo = self.pageNo

        industry_name_list = []
        for industry_code in industry_code_list:
            industry_name_list.append(
                {'industry_name': self.industry_code_dic[industry_code],
                 'industry_code': str(industry_code),
                 'page_size': pageSize
                 }
            )
        for industry in industry_name_list:
            industry_name = industry['industry_name']
            child_dir_name = os.path.join(dir_name, industry_name)
            os.makedirs(child_dir_name, exist_ok=True)
            industry_code = industry['industry_code']
            self.__download_report(dir_name=child_dir_name, industry_name=industry_name, industryCode=industry_code,
                                   beginTime=beginTime, endTime=endTime, pageSize=pageSize, pageNo=pageNo,
                                   is_download_pdf=is_download_pdf)

    def asser_industry_code_list(self, industry_code_list):
        for industry_code in industry_code_list:
            if str(industry_code) not in self.industry_code_dic:
                raise Exception('无效行业代码{}'.format(industry_code))

    def gen_readme_file(self):
        with open('README.md', 'w', encoding='utf-8') as readme_file:
            readme_file.write('# eastmoney\n 东方财富行业研报，每天自动更新\n\n\n')
            for industry in self.industry_name_list:
                file_name = industry['industry_name']
                child_dir = self.dir_name + '/' + file_name
                url = '{}/{}'.format(child_dir, file_name + '.csv')
                readme_file.write('[`{}`]({})  '.format(file_name, url))


if __name__ == '__main__':
    reportHelper = EastMoneyReport('gen')
    reportHelper.download_report_all()
    # reportHelper.download_report(['*', '1030', '1045'], pageSize=10, is_download_pdf=True)
    # reportHelper.gen_readme_file()
    print('done')
