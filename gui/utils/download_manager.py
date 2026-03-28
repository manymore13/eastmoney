#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
东方财富研报工具 - 下载管理器
多线程下载研报PDF，支持队列管理
"""

import os
import time
import subprocess
import threading
import requests
import re
from datetime import datetime

from PySide6.QtCore import QObject, Signal, QThread, QMutex


# PDF链接缓存
_pdf_url_cache = {}


class DownloadTask:
    """下载任务类"""

    def __init__(self, report, output_dir):
        self.report = report
        self.output_dir = output_dir
        self.status = "pending"  # pending, downloading, completed, failed
        self.progress = 0
        self.filename = ""
        self.error = ""


class DownloadWorker(QThread):
    """下载工作线程"""

    progress_signal = Signal(str, int, int)  # (filename, current, total)
    finished_signal = Signal(str, bool)  # (filename, success)

    def __init__(self, task, client):
        super().__init__()
        self.task = task
        self.client = client

    def run(self):
        """执行下载"""
        try:
            self.task.status = "downloading"

            report = self.task.report
            output_dir = self.task.output_dir

            # 获取标题作为文件名
            title = report.get("title", "未命名")
            # 清理文件名中的非法字符
            filename = self.clean_filename(title)
            if not filename:
                filename = "report"

            # 获取研报类型 - 优先使用传递的 report_type，否则根据 column 字段判断
            report_type = report.get("_report_type", "industry")
            column = report.get("column", "")
            
            # 如果 report_type 未知，根据 column 字段判断
            if not report_type or report_type == "industry":
                if column == "002001001":
                    report_type = "macro"
                elif column == "002001002":
                    report_type = "strategy"
                elif column == "002003001":
                    report_type = "morning"
                elif column == "002002003002":
                    report_type = "industry"

            # 创建输出目录
            type_dir = os.path.join(output_dir, report_type)
            os.makedirs(type_dir, exist_ok=True)
            pdf_path = os.path.join(type_dir, f'{filename}.pdf')

            # 获取PDF链接 - 需要抓取网页获取真正的PDF链接
            self.progress_signal.emit(filename, 1, 3)

            # 根据类型选择正确的URL模板和字段
            info_code = report.get("infoCode", "")
            encode_url = report.get("encodeUrl", "")

            # 构建网页URL
            if report_type == "industry":
                web_url = f"https://data.eastmoney.com/report/zw_industry.jshtml?infocode={info_code}"
            elif report_type == "strategy":
                web_url = f"https://data.eastmoney.com/report/zw_strategy.jshtml?encodeUrl={encode_url}"
            elif report_type == "macro":
                web_url = f"https://data.eastmoney.com/report/zw_macro.jshtml?infocode={info_code}"
            elif report_type == "morning":
                web_url = f"https://data.eastmoney.com/report/zw_morning.jshtml?encodeUrl={encode_url}"
            else:
                web_url = f"https://data.eastmoney.com/report/zw_industry.jshtml?infocode={info_code}"

            # 抓取网页获取PDF链接
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                resp = requests.get(web_url, headers=headers, timeout=15)
                if resp.status_code == 200:
                    # 从网页中提取PDF链接
                    pdf_links = re.findall(r'https://pdf\.dfcfw\.com/pdf/[^\"\'<>\s]+\.pdf', resp.text)
                    if pdf_links:
                        pdf_url = pdf_links[0]
                    else:
                        self.task.status = "failed"
                        self.task.error = "网页中未找到PDF链接"
                        self.finished_signal.emit(filename, False)
                        return
                else:
                    self.task.status = "failed"
                    self.task.error = f"访问网页失败: {resp.status_code}"
                    self.finished_signal.emit(filename, False)
                    return
            except Exception as e:
                self.task.status = "failed"
                self.task.error = f"获取PDF链接失败: {str(e)}"
                self.finished_signal.emit(filename, False)
                return

            # 下载PDF
            self.progress_signal.emit(filename, 2, 3)
            result = self.client.download_pdf(pdf_url, pdf_path)

            self.progress_signal.emit(filename, 3, 3)

            if result and os.path.exists(pdf_path):
                # 验证PDF文件有效性
                with open(pdf_path, 'rb') as f:
                    header = f.read(4)
                if header == b'%PDF':
                    self.task.filename = os.path.basename(pdf_path)
                    self.task.status = "completed"
                    self.finished_signal.emit(self.task.filename, True)
                else:
                    self.task.status = "failed"
                    self.task.error = "下载文件无效"
                    self.finished_signal.emit(filename, False)
            else:
                self.task.status = "failed"
                self.task.error = "下载失败"
                self.finished_signal.emit(filename, False)

        except Exception as e:
            self.task.status = "failed"
            self.task.error = str(e)
            self.finished_signal.emit(self.task.filename if self.task.filename else "未知文件", False)

    def clean_filename(self, filename):
        """清理文件名中的非法字符"""
        illegal_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in illegal_chars:
            filename = filename.replace(char, '_')
        # 限制长度
        if len(filename) > 200:
            filename = filename[:200]
        return filename


class DownloadManager(QObject):
    """下载管理器"""

    progress_signal = Signal(str, int, int)  # (filename, current, total)
    finished_signal = Signal(str, bool)  # (filename, success)
    queue_updated_signal = Signal(int)  # 队列更新

    def __init__(self, max_concurrent=3):
        super().__init__()
        self.max_concurrent = max_concurrent
        self.queue = []
        self.active_workers = []
        self.client = None

        # 导入report_client
        from report_client import EastMoneyReportClient
        self.client = EastMoneyReportClient()

        # 线程锁
        self.mutex = QMutex()

    def add_task(self, report, output_dir):
        """添加下载任务"""
        task = DownloadTask(report, output_dir)
        self.queue.append(task)
        self.queue_updated_signal.emit(len(self.queue))

        # 尝试启动下载
        self.process_queue()

    def process_queue(self):
        """处理下载队列"""
        self.mutex.lock()

        # 清理已完成的线程
        self.active_workers = [w for w in self.active_workers if w.isRunning()]

        # 如果有空闲位置，启动新任务
        while len(self.active_workers) < self.max_concurrent and self.queue:
            # 找到pending任务
            task = None
            for t in self.queue:
                if t.status == "pending":
                    task = t
                    break

            if not task:
                break

            # 创建工作线程
            worker = DownloadWorker(task, self.client)
            worker.progress_signal.connect(self.on_worker_progress)
            worker.finished_signal.connect(self.on_worker_finished)
            worker.finished.connect(lambda: None)  # 忽略无参信号
            worker.start()
            self.active_workers.append(worker)

        self.mutex.unlock()

    def on_worker_progress(self, filename, current, total):
        """工作线程进度"""
        self.progress_signal.emit(filename, current, total)

    def on_worker_finished(self, filename, success):
        """工作线程完成"""
        self.finished_signal.emit(filename, success)
        # 继续处理队列
        self.process_queue()

    def clear_queue(self):
        """清空队列"""
        self.queue = [t for t in self.queue if t.status == "downloading"]
        self.queue_updated_signal.emit(len(self.queue))

    def get_queue_status(self):
        """获取队列状态"""
        pending = sum(1 for t in self.queue if t.status == "pending")
        downloading = sum(1 for t in self.queue if t.status == "downloading")
        completed = sum(1 for t in self.queue if t.status == "completed")
        failed = sum(1 for t in self.queue if t.status == "failed")

        return {
            "pending": pending,
            "downloading": downloading,
            "completed": completed,
            "failed": failed,
            "total": len(self.queue)
        }
