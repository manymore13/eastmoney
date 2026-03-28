#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
使用Selenium下载东方财富研报PDF
"""

import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_pdf_url_with_selenium(report_url):
    """
    使用Selenium从研报页面获取PDF下载链接
    """
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    driver = None
    try:
        driver = webdriver.Edge(options=options)
        driver.get(report_url)
        
        # 等待页面加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "to-link"))
        )
        
        # 查找PDF链接
        pdf_link_elem = driver.find_element(By.CSS_SELECTOR, "span.to-link a.pdf-link")
        pdf_url = pdf_link_elem.get_attribute("href")
        
        return pdf_url
        
    except Exception as e:
        print(f"Selenium获取PDF链接失败: {e}")
        return None
        
    finally:
        if driver:
            driver.quit()


def download_pdf_with_selenium(pdf_url, save_path):
    """
    使用Selenium下载PDF文件
    """
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    # 设置下载目录
    download_dir = os.path.dirname(save_path) or '.'
    prefs = {
        "download.default_directory": os.path.abspath(download_dir),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
    }
    options.add_experimental_option("prefs", prefs)
    
    driver = None
    try:
        driver = webdriver.Edge(options=options)
        driver.get(pdf_url)
        
        # 等待下载完成
        time.sleep(3)
        
        # 检查文件是否下载成功
        filename = os.path.basename(save_path)
        downloaded_files = os.listdir(download_dir)
        
        # 查找刚下载的文件
        for f in downloaded_files:
            if f.endswith('.pdf') or f.startswith('Untitled'):
                actual_path = os.path.join(download_dir, f)
                if os.path.getsize(actual_path) > 1000:  # 大于1KB可能是有效PDF
                    # 重命名为目标文件名
                    if f != filename:
                        if os.path.exists(save_path):
                            os.remove(save_path)
                        os.rename(actual_path, save_path)
                    return True
        
        return False
        
    except Exception as e:
        print(f"Selenium下载失败: {e}")
        return False
        
    finally:
        if driver:
            driver.quit()


if __name__ == '__main__':
    # 测试
    url = 'https://data.eastmoney.com/report/zw_industry.jshtml?infocode=AP202603261820768615'
    pdf_url = get_pdf_url_with_selenium(url)
    print(f"PDF URL: {pdf_url}")
