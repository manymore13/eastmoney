import csv
import json
import os
import re
import time

import requests


class EastMoneyReport:
    east_money_url = 'https://reportapi.eastmoney.com/report/list?cb=datatable1808538&industryCode={' \
                     'industryCode}&pageSize={pageSize}&industry=*&rating=*&ratingChange=*&beginTime={' \
                     'beginTime}&endTime={endTime}&pageNo={pageNo}&fields=&qType=1&orgCode=&rcode=&_={time}'

    report_info_url = 'https://data.eastmoney.com/report/zw_industry.jshtml?infocode='

    def __init__(self):
        self.beginTime = '2021-05-14'
        self.endTime = '2023-05-14'
        self.pageSize = '50'
        self.industryCode = '1046'
        self.pageNo = '1'

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
    def get_report_json(self, report_json_url):
        report_content = requests.get(report_json_url).text
        report_content = re.search('\((.+)\)', report_content).group(1)
        return report_content

    @classmethod
    def save_json(self, dir_name, report_name, content):
        with open(os.path.join(dir_name, report_name + '.json'), 'w', encoding='utf-8') as file:
            file.write(content)

    def save_csv(self, dir_name, report_name, content_json):
        report_list = json.loads(content_json)['data']
        report_list_data = []
        for report in report_list:
            report_data = {'研报名称': report['title'], '机构名称': report['orgSName'],
                           '发布时间': report['publishDate'], '行业': report['industryName'],
                           '研报地址': self.report_info_url + report['infoCode']}
            report_list_data.append(report_data)

        with open(os.path.join(dir_name, report_name + '.csv'), 'w', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['研报名称', '机构名称', '发布时间', '行业', '研报地址'])
            writer.writeheader()
            writer.writerows(report_list_data)

    def download_report(self, dir_name, report_name, report_json_url):
        content_json = self.get_report_json(report_json_url)
        # self.save_json(dir_name, report_name, content_json)
        self.save_csv(dir_name, report_name, content_json)


def gen_readme_file(industry_name_list):
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write('')


if __name__ == '__main__':
    file_name = 'industry.json'
    with open(file_name, 'r', encoding='utf-8') as f:
        industry_name_list = json.load(f)

    report = EastMoneyReport()
    # json.loads()
    # industry_name_list = [['游戏行业', 1046], ['保险', 474], ['房地产服务', 1045], ['不限行业', '*']]
    dir_name = 'gen'
    os.makedirs(dir_name, exist_ok=True)
    for industry in industry_name_list:
        file_name = industry[0]
        industry_code = industry[1]
        json_url = report.build_url(industryCode=industry_code)
        report.download_report(dir_name, file_name, json_url)
    print('done')
