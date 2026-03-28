#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
东方财富研报工具 - GUI主入口
使用PySide6构建跨平台桌面应用
"""

import sys
import os

# 添加项目根目录到路径，以便导入report_client
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from gui.main_window import MainWindow


def main():
    """主入口函数"""
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("东方财富研报工具")
    app.setOrganizationName("EastMoney")
    app.setOrganizationDomain("eastmoney.com")

    # 设置应用程序样式
    app.setStyle("Fusion")

    # 创建并显示主窗口
    window = MainWindow()
    window.show()

    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
