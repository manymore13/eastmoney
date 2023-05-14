import requests
import time
import re
import json
import os
import csv


class EastMoneyReport:
    east_money_url = 'https://reportapi.eastmoney.com/report/list?cb=datatable1808538&industryCode={industryCode}&pageSize={pageSize}&industry=*&rating=*&ratingChange=*&beginTime={beginTime}&endTime={endTime}&pageNo={pageNo}&fields=&qType=1&orgCode=&rcode=&_={time}'
    report_info_url = 'https://data.eastmoney.com/report/zw_industry.jshtml?infocode='
    cur_report_url = ''

    def __init__(self):
        self.beginTime = '2021-05-14'
        self.endTime = '2023-05-14'
        self.pageSize = '50'
        self.industryCode = '1046'
        self.pageNo = '1'

    def __update_url(self, industryCode=None, beginTime=None, endTime=None, pageSize=None, pageNo=None):
        if (beginTime is None):
            beginTime = self.beginTime

        if (beginTime is None):
            beginTime = self.beginTime

        if (endTime is None):
            endTime = self.endTime

        if (pageSize is None):
            pageSize = self.pageSize

        if (pageNo is None):
            pageNo = self.pageNo

        if (industryCode is None):
            industryCode = self.industryCode

        cur_time = int(time.time())
        self.cur_report_url = self.east_money_url.format(industryCode=industryCode, pageSize=pageSize,
                                                         beginTime=beginTime,
                                                         endTime=endTime, pageNo=pageNo, time=cur_time)
        print(self.cur_report_url)
        return self.cur_report_url

    def get_report_json(self, industryCode=None, beginTime=None, endTime=None, pageSize=None, pageNo=None):
        self.__update_url(industryCode, beginTime, endTime, pageSize, pageNo)
        report_content = requests.get(self.cur_report_url).text
        report_content = re.search('\((.+)\)', report_content).group(1)
        return report_content

    def save_json(self, report_name, content):
        with open(os.path.join('.', report_name + '.json'), 'w', encoding='utf-8') as file:
            file.write(content)

    def save_csv(self, report_name, content_json):
        reportlist = json.loads(content_json)['data']
        report_list_data = []
        for report in reportlist:
            report_data = {'研报名称': report['title'], '机构名称': report['orgSName'],
                           '发布时间': report['publishDate'], '行业': report['industryName'],
                           '研报地址': self.report_info_url + report['infoCode']}
            report_list_data.append(report_data)

        with open(report_name + '.csv', 'w', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['研报名称', '机构名称', '发布时间', '行业', '研报地址'])
            writer.writeheader()
            writer.writerows(report_list_data)

    def save(self, report_name, content_json):
        self.save_json(report_name, content_json)
        self.save_csv(report_name, content_json)


if __name__ == '__main__':
    report = EastMoneyReport()

    industry_name_list = [['游戏行业', 1046], ['保险', 474], ['房地产服务', 1045]]
    for industry in industry_name_list:
        file_name = industry[0]
        industry_code = industry[1]
        report_json = report.get_report_json(industryCode=industry_code)
        report.save(file_name, report_json)
    print('done')

    # print(requests.get('https://reportapi.eastmoney.com/report/list?cb=datatable1808538&industryCode=1046&pageSize=50&industry=*&rating=*&ratingChange=*&beginTime=2021-05-14&endTime=2023-05-14&pageNo=1&fields=&qType=1&orgCode=&rcode=&_=1684069265811').text)
    #                    'https://reportapi.eastmoney.com/report/list?cb=datatable1808538&industryCode=1046&pageSize=50&industry=*&rating=*&ratingChange=*&beginTime=2023-05-14&endTime=2023-05-14&pageNo=1&fields=&qType=1&orgCode=&rcode=&_=1684069265811'
