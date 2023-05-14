import requests
import time
import re
import json
import os


class EastMoneyReport:
    east_money_url = 'https://reportapi.eastmoney.com/report/list?cb=datatable1808538&industryCode={industryCode}&pageSize={pageSize}&industry=*&rating=*&ratingChange=*&beginTime={beginTime}&endTime={endTime}&pageNo={pageNo}&fields=&qType=1&orgCode=&rcode=&_={time}'
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

    def save(self, report_name, content):
        with open(os.path.join('.', report_name + '.json'), 'w', encoding='utf-8') as file:
            file.write(content)


if __name__ == '__main__':
    report = EastMoneyReport()
    report_json = report.get_report_json()
    report.save('行业研报', report_json)
    print(report_json)

    # print(requests.get('https://reportapi.eastmoney.com/report/list?cb=datatable1808538&industryCode=1046&pageSize=50&industry=*&rating=*&ratingChange=*&beginTime=2021-05-14&endTime=2023-05-14&pageNo=1&fields=&qType=1&orgCode=&rcode=&_=1684069265811').text)
    #                    'https://reportapi.eastmoney.com/report/list?cb=datatable1808538&industryCode=1046&pageSize=50&industry=*&rating=*&ratingChange=*&beginTime=2023-05-14&endTime=2023-05-14&pageNo=1&fields=&qType=1&orgCode=&rcode=&_=1684069265811'
