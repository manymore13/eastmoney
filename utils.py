import json

from selenium import webdriver
from selenium.webdriver.common.by import By


def load_industry_json():
    # 生产行业id
    start_url = 'https://data.eastmoney.com/report/industry.jshtml'

    driver = webdriver.Edge()
    driver.get(start_url)
    driver.implicitly_wait(0.5)
    element_li_list = driver.find_elements(by=By.XPATH, value='//*[@data-bkval]')
    industry_info_list = []

    for ele_li in element_li_list:
        industry_name = ele_li.get_attribute('textContent')
        page_size = 100
        if industry_name == '不限':
            industry_name = '全行业'
            page_size = 200
        else:
            page_size = 100
        industry_code = ele_li.get_attribute("data-bkval")
        industry_info = [industry_name, industry_code, page_size]
        industry_info_list.append(industry_info)
        # print('tag_name = {},tag_text = {},data-bkval={},is_display = {}'.format(ele_li.tag_name, industry_name, industry_code,ele_li.is_displayed()))

    file_name = 'industry.json'

    # 保存行业json文件
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(industry_info_list, file)

    print(industry_info_list)
    print('done')


if __name__ == '__main__':
    load_industry_json()
