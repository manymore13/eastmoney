import csv
import json

from selenium import webdriver
from selenium.webdriver.common.by import By

import os


def download_report(self, dir_name, industry_name, industryCode=None, beginTime=None, endTime=None, pageSize=None,
                      pageNo=None, is_download_pdf=False):
    delete_all_files(dir_name)
    report_json_url = self.build_url(industryCode, beginTime, endTime, pageSize, pageNo)
    content_json = self.get_report_json(report_json_url)
    self.save_csv_and_pdf(dir_name, industry_name, content_json, is_download_pdf)

def delete_all_files(dir_name):
    for f in os.listdir(dir_name):
        os.remove(os.path.join(dir_name, f))


def load_industry_json():
    # 生产行业id
    start_url = 'https://data.eastmoney.com/report/industry.jshtml'

    driver = webdriver.Edge()
    driver.get(start_url)
    driver.implicitly_wait(0.5)
    element_li_list = driver.find_elements(by=By.XPATH, value='//*[@data-bkval]')
    industry_info_list = []
    csv_head = ['行业名称', '行业代码']
    csv_industry_info_list = []
    for ele_li in element_li_list:
        industry_name = ele_li.get_attribute('textContent')
        page_size = 100
        if industry_name == '不限':
            industry_name = '全行业'
            page_size = 200
        else:
            page_size = 100
        industry_code = ele_li.get_attribute("data-bkval")
        industry_info = {'industry_name': industry_name, 'industry_code': industry_code, 'page_size': page_size}
        industry_info_list.append(industry_info)

        csv_industry_info = {csv_head[0]: industry_name, csv_head[1]: industry_code}
        csv_industry_info_list.append(csv_industry_info)
        # print('tag_name = {},tag_text = {},data-bkval={},is_display = {}'.format(ele_li.tag_name, industry_name, industry_code,ele_li.is_displayed()))
    file_name = 'industry.json'

    # 保存行业json文件
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(industry_info_list, file)

    # 保存行业 csv文件
    with open('industry.csv', 'w', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=csv_head)
        writer.writeheader()
        writer.writerows(csv_industry_info_list)

    print(industry_info_list)
    print('done')


if __name__ == '__main__':
    load_industry_json()
