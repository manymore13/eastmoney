#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
东方财富研报工具 - 主窗口
整合行业列表、研报查询、下载管理等功能
"""

import json
import os
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTreeWidget, QTreeWidgetItem, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QComboBox, QLabel, QProgressBar,
    QHeaderView, QAbstractItemView, QMessageBox,
    QFileDialog, QApplication
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QColor, QFont, QAction, QPalette, QIcon

from report_client import EastMoneyReportClient
from gui.utils.download_manager import DownloadManager


# 现代配色方案
class Colors:
    """配色方案"""
    PRIMARY = "#2563EB"        # 主色 - 蓝色
    PRIMARY_HOVER = "#1D4ED8"  # 主色悬停
    SUCCESS = "#10B981"        # 成功 - 绿色
    WARNING = "#F59E0B"        # 警告 - 橙色
    DANGER = "#EF4444"         # 危险 - 红色
    BG_MAIN = "#F8FAFC"        # 主背景
    BG_CARD = "#FFFFFF"        # 卡片背景
    BG_SIDEBAR = "#1E293B"     # 侧边栏背景
    TEXT_MAIN = "#1E293B"      # 主文字
    TEXT_SECONDARY = "#64748B" # 次要文字
    TEXT_LIGHT = "#F1F5F9"     # 浅色文字
    BORDER = "#E2E8F0"         # 边框


class ModernButton(QPushButton):
    """现代风格按钮，支持防抖"""

    def __init__(self, text, primary=False, parent=None):
        super().__init__(text, parent)
        self.primary = primary
        self.setCursor(Qt.PointingHandCursor)
        # 使用支持中文的字体，字体稍小一点
        font = QFont()
        font.setFamily("Microsoft YaHei, SimHei, Arial")
        font.setPointSize(9)
        self.setFont(font)
        self.init_style()
        
        # 防抖相关
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_duration = 800  # 毫秒

    def set_debounce_duration(self, ms):
        """设置防抖时间（毫秒）"""
        self._debounce_duration = ms

    def debounce_click(self, slot):
        """带防抖的点击连接"""
        def wrapped():
            if not self.isEnabled():
                return
            self.setEnabled(False)
            # 断开之前的定时器连接
            try:
                self._debounce_timer.timeout.disconnect()
            except:
                pass
            # 定时器到期后重新启用按钮
            self._debounce_timer.timeout.connect(lambda: self.setEnabled(True))
            self._debounce_timer.start(self._debounce_duration)
            # 执行操作
            slot()

        # 先断开之前的连接
        try:
            self.clicked.disconnect()
        except:
            pass
        self.clicked.connect(wrapped)

    def init_style(self):
        if self.primary:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Colors.PRIMARY};
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 6px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {Colors.PRIMARY_HOVER};
                }}
                QPushButton:pressed {{
                    background-color: #1E40AF;
                }}
                QPushButton:disabled {{
                    background-color: #94A3B8;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: white;
                    color: {Colors.TEXT_MAIN};
                    border: 1px solid {Colors.BORDER};
                    padding: 6px 12px;
                    border-radius: 6px;
                }}
                QPushButton:hover {{
                    background-color: #F1F5F9;
                    border-color: {Colors.PRIMARY};
                }}
            """)


class MainWindow(QWidget):
    """主窗口类"""

    # 信号定义
    query_finished = Signal(list)
    download_progress = Signal(str, int, int)
    download_finished = Signal(str, bool)

    def __init__(self):
        super().__init__()
        self.client = EastMoneyReportClient()
        self.download_manager = DownloadManager()

        # 研报数据缓存
        self.current_reports = []
        self.current_page = 1
        self.total_pages = 1
        self.current_industry_code = None
        self.current_report_type = "industry"

        # 待下载列表
        self.download_list = []  # 已选中的研报列表
        self._processing_checkbox = False  # 防止重复处理
        self._checked_reports = {}  # 保存勾选状态 {report_id: True/False}

        # 行业数据
        self.industry_data = {}

        # 分页大小
        self.page_size = 20

        # 初始化UI
        self.init_ui()
        self.load_industry_data()
        self.connect_signals()

    def init_ui(self):
        """初始化UI布局"""
        self.setWindowTitle("东方财富研报工具")
        self.setGeometry(150, 100, 1100, 700)
        self.setStyleSheet(f"background-color: {Colors.BG_MAIN};")

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 顶部导航栏
        self.create_title_bar(main_layout)

        # 中央分割器
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {Colors.BORDER};
            }}
        """)

        # 左侧：行业分类（深色背景）
        left_panel = self.create_industry_panel()
        left_panel.setStyleSheet(f"background-color: {Colors.BG_SIDEBAR};")
        splitter.addWidget(left_panel)

        # 右侧：研报列表
        right_panel = self.create_report_panel()
        splitter.addWidget(right_panel)

        splitter.setStretchFactor(0, 220)
        splitter.setStretchFactor(1, 880)

        main_layout.addWidget(splitter)

        # 底部状态栏
        self.create_status_bar(main_layout)

    def create_title_bar(self, parent_layout):
        """创建顶部导航栏"""
        title_bar = QWidget()
        title_bar.setStyleSheet(f"""
            background-color: white;
            border-bottom: 1px solid {Colors.BORDER};
        """)
        title_bar.setFixedHeight(60)

        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(20, 0, 20, 0)

        # Logo/标题
        title = QLabel("📊 东方财富研报")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1E293B;")
        layout.addWidget(title)

        layout.addStretch()

        # 研报类型选择
        layout.addWidget(QLabel("类型:"))
        self.report_type_combo = QComboBox()
        self.report_type_combo.setFixedWidth(120)
        self.report_type_combo.addItems([
            "行业研报",
            "个股研报",
            "策略报告",
            "宏观研究",
            "券商晨报"
        ])
        self.report_type_combo.setCurrentText("行业研报")
        self.report_type_combo.currentTextChanged.connect(lambda _: self.on_type_changed())
        layout.addWidget(self.report_type_combo)

        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setFixedWidth(150)
        self.search_input.setPlaceholderText("搜索股票/机构...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 6px 12px;
                border: 1px solid {Colors.BORDER};
                border-radius: 6px;
                background: {Colors.BG_MAIN};
            }}
            QLineEdit:focus {{
                border-color: {Colors.PRIMARY};
            }}
        """)
        self.search_input.returnPressed.connect(self.on_search)
        layout.addWidget(self.search_input)

        # 时间范围选择
        layout.addWidget(QLabel("时间:"))
        self.time_range_combo = QComboBox()
        self.time_range_combo.setFixedWidth(100)
        self.time_range_combo.addItems([
            "当月",
            "近1月",
            "近3月",
            "近半年",
            "近1年",
            "近2年",
            "全部"
        ])
        self.time_range_combo.setCurrentText("近半年")
        self.time_range_combo.currentTextChanged.connect(lambda _: self.on_search())
        layout.addWidget(self.time_range_combo)

        # 搜索按钮
        search_btn = ModernButton("搜索", primary=True)
        search_btn.setFixedWidth(60)
        search_btn.set_debounce_duration(1000)
        search_btn.debounce_click(self.on_search)
        layout.addWidget(search_btn)

        layout.addSpacing(10)

        # 下载目录
        layout.addWidget(QLabel("📁"))
        self.download_path_input = QLineEdit()
        self.download_path_input.setText(self.get_default_download_path())
        self.download_path_input.setFixedWidth(250)
        self.download_path_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 6px 12px;
                border: 1px solid {Colors.BORDER};
                border-radius: 6px;
                background: {Colors.BG_MAIN};
            }}
        """)
        layout.addWidget(self.download_path_input)

        browse_btn = ModernButton("选择")
        browse_btn.setFixedWidth(60)
        browse_btn.clicked.connect(self.on_select_download_path)
        layout.addWidget(browse_btn)

        parent_layout.addWidget(title_bar)

    def create_industry_panel(self):
        """创建行业分类面板"""
        panel = QWidget()
        panel.setMinimumWidth(200)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 15, 0, 15)
        layout.setSpacing(5)

        # 标题
        title = QLabel("行业分类")
        title.setStyleSheet(f"""
            color: {Colors.TEXT_LIGHT};
            font-size: 13px;
            font-weight: bold;
            padding: 0 15px;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)

        # 行业树
        self.industry_tree = QTreeWidget()
        self.industry_tree.setStyleSheet(f"""
            QTreeWidget {{
                background-color: transparent;
                color: {Colors.TEXT_LIGHT};
                border: none;
                outline: none;
            }}
            QTreeWidget::item {{
                padding: 8px 15px;
                border-radius: 4px;
                margin: 2px 8px;
            }}
            QTreeWidget::item:hover {{
                background-color: rgba(255, 255, 255, 0.1);
            }}
            QTreeWidget::item:selected {{
                background-color: {Colors.PRIMARY};
            }}
            QTreeWidget::branch {{
                background-color: transparent;
            }}
        """)
        self.industry_tree.setHeaderHidden(True)
        self.industry_tree.setIndentation(12)
        self.industry_tree.itemClicked.connect(self.on_industry_clicked)
        layout.addWidget(self.industry_tree)

        return panel

    def create_report_panel(self):
        """创建研报列表面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)

        # 研报列表标题栏
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        self.list_title = QLabel("📄 研报列表")
        self.list_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #1E293B;")
        header_layout.addWidget(self.list_title)

        header_layout.addStretch()

        # 刷新按钮
        refresh_btn = ModernButton("🔄 刷新")
        refresh_btn.setFixedWidth(80)
        refresh_btn.set_debounce_duration(1000)
        refresh_btn.debounce_click(self.on_refresh)
        header_layout.addWidget(refresh_btn)

        layout.addWidget(header)

        # 研报表格
        self.report_table = QTableWidget()
        self.report_table.setColumnCount(6)
        self.report_table.setHorizontalHeaderLabels([
            "", "标题", "机构", "公司名称", "发布日期", "操作"
        ])
        # 设置列宽
        self.report_table.setColumnWidth(0, 40)   # 选择框
        self.report_table.setColumnWidth(1, 350)  # 标题
        self.report_table.setColumnWidth(2, 100)  # 机构
        self.report_table.setColumnWidth(3, 80)   # 公司名称
        self.report_table.setColumnWidth(4, 90)   # 发布日期
        self.report_table.setColumnWidth(5, 80)  # 下载
        self.report_table.horizontalHeader().setStretchLastSection(True)

        self.report_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.report_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.report_table.setShowGrid(False)
        self.report_table.verticalHeader().setDefaultSectionSize(40)

        # 表格样式
        self.report_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: white;
                border: 1px solid {Colors.BORDER};
                border-radius: 8px;
                outline: none;
            }}
            QTableWidget::item {{
                padding: 8px 12px;
                border-bottom: 1px solid {Colors.BORDER};
            }}
            QTableWidget::item:selected {{
                background-color: rgba(37, 99, 235, 0.1);
                color: {Colors.PRIMARY};
            }}
            QHeaderView::section {{
                background-color: {Colors.BG_MAIN};
                color: {Colors.TEXT_SECONDARY};
                padding: 10px;
                border: none;
                border-bottom: 1px solid {Colors.BORDER};
                font-weight: bold;
                font-size: 12px;
            }}
            QTableWidget::item:hover {{
                background-color: #E2E8F0;
                color: #1E293B;
            }}
            QTableWidget::item:selected {{
                background-color: rgba(37, 99, 235, 0.15);
                color: #1E40AF;
            }}
        """)

        # 表头
        header = self.report_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # 选择框固定宽度
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # 标题自动拉伸
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setFixedHeight(40)

        # 双击下载
        self.report_table.itemDoubleClicked.connect(self.on_row_double_clicked)

        # 复选框状态改变信号
        self.report_table.itemChanged.connect(self.on_item_changed)

        layout.addWidget(self.report_table)

        # 分页控件
        page_widget = QWidget()
        page_layout = QHBoxLayout(page_widget)
        page_layout.setContentsMargins(0, 0, 0, 0)

        self.page_label = QLabel("共 0 条记录，第 1/1 页")
        self.page_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        page_layout.addWidget(self.page_label)

        page_layout.addStretch()

        # 首页/上一页
        first_btn = ModernButton("首页")
        first_btn.setFixedWidth(60)
        first_btn.set_debounce_duration(200)
        first_btn.debounce_click(self.on_first_page)
        page_layout.addWidget(first_btn)

        prev_btn = ModernButton("◀")
        prev_btn.setFixedWidth(40)
        prev_btn.set_debounce_duration(200)
        prev_btn.debounce_click(self.on_prev_page)
        page_layout.addWidget(prev_btn)

        # 下一页/末页
        next_btn = ModernButton("▶")
        next_btn.setFixedWidth(40)
        next_btn.set_debounce_duration(200)
        next_btn.debounce_click(self.on_next_page)
        page_layout.addWidget(next_btn)

        last_btn = ModernButton("末页")
        last_btn.setFixedWidth(60)
        last_btn.set_debounce_duration(200)
        last_btn.debounce_click(self.on_last_page)
        page_layout.addWidget(last_btn)

        page_layout.addSpacing(20)

        # 每页数量
        page_layout.addWidget(QLabel("每页:"))
        self.page_size_combo = QComboBox()
        self.page_size_combo.setFixedWidth(60)
        self.page_size_combo.addItems(["10", "20", "50"])
        self.page_size_combo.setCurrentText("20")
        self.page_size_combo.currentTextChanged.connect(self.on_page_size_changed)
        page_layout.addWidget(self.page_size_combo)

        layout.addWidget(page_widget)

        # 批量下载栏
        batch_widget = QWidget()
        batch_layout = QHBoxLayout(batch_widget)
        batch_layout.setContentsMargins(0, 5, 0, 5)

        batch_layout.addStretch()

        # 批量下载按钮
        batch_download_btn = ModernButton("⬇ 批量下载", primary=True)
        batch_download_btn.setFixedWidth(120)
        batch_download_btn.set_debounce_duration(1500)
        batch_download_btn.debounce_click(self.on_batch_download)
        batch_layout.addWidget(batch_download_btn)

        layout.addWidget(batch_widget)

        return panel

    def create_status_bar(self, parent_layout):
        """创建底部状态栏"""
        status_bar = QWidget()
        status_bar.setStyleSheet(f"""
            background-color: white;
            border-top: 1px solid {Colors.BORDER};
        """)
        status_bar.setFixedHeight(36)

        layout = QHBoxLayout(status_bar)
        layout.setContentsMargins(20, 0, 20, 0)

        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;")
        layout.addWidget(self.status_label)

        layout.addStretch()

        # 待下载列表入口 - 使用按钮样式
        self.download_list_btn = QPushButton("📥 待下载(0)")
        self.download_list_btn.setFlat(True)  # 扁平样式
        self.download_list_btn.setCursor(Qt.PointingHandCursor)
        self.download_list_btn.setStyleSheet(f"""
            QPushButton {{
                color: {Colors.TEXT_SECONDARY};
                font-size: 12px;
                background-color: transparent;
                border: none;
                padding: 4px 10px;
                text-align: left;
            }}
            QPushButton:hover {{
                color: {Colors.PRIMARY};
                background-color: #F1F5F9;
                border-radius: 4px;
            }}
        """)
        self.download_list_btn.clicked.connect(self.show_download_list_panel)
        layout.addWidget(self.download_list_btn)

        # 下载进度
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(200)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {Colors.BORDER};
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background-color: {Colors.PRIMARY};
                border-radius: 3px;
            }}
        """)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # 下载状态
        self.download_status_label = QLabel("")
        self.download_status_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;")
        layout.addWidget(self.download_status_label)

        parent_layout.addWidget(status_bar)

    def connect_signals(self):
        """连接信号槽"""
        self.download_manager.progress_signal.connect(self.on_download_progress)
        self.download_manager.finished_signal.connect(self.on_download_finished)

    def load_industry_data(self):
        """加载行业数据"""
        industry_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "industry.json"
        )

        try:
            with open(industry_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.industry_data = data
            self.industry_tree.clear()

            # 添加根节点 - 全部行业
            root = QTreeWidgetItem(self.industry_tree, ["📈 全部行业"])
            root.setData(0, Qt.UserRole, {"type": "all"})

            # 添加子节点
            for item in data:
                child = QTreeWidgetItem(root, [item.get('industry_name', '')])
                child.setData(0, Qt.UserRole, {
                    "type": "industry",
                    "code": item.get("industry_code"),
                    "name": item.get("industry_name")
                })

            root.setExpanded(True)

            # 默认查询第一个行业
            if data:
                self.current_industry_code = data[0].get("code")
                QTimer.singleShot(100, self.query_reports)

        except Exception as e:
            self.status_label.setText(f"加载行业数据失败: {str(e)}")

    def get_report_type(self):
        """获取当前选中的研报类型"""
        type_map = {
            "行业研报": "industry",
            "个股研报": "stock",
            "策略报告": "strategy",
            "宏观研究": "macro",
            "券商晨报": "morning"
        }
        return type_map.get(self.report_type_combo.currentText(), "industry")

    def get_time_range(self):
        """获取时间范围"""
        from datetime import datetime, timedelta

        now = datetime.now()
        text = self.time_range_combo.currentText()

        if text == "当月":
            begin_time = now.replace(day=1).strftime('%Y-%m-%d')
            end_time = now.strftime('%Y-%m-%d')
        elif text == "近1月":
            begin_time = (now - timedelta(days=30)).strftime('%Y-%m-%d')
            end_time = now.strftime('%Y-%m-%d')
        elif text == "近3月":
            begin_time = (now - timedelta(days=90)).strftime('%Y-%m-%d')
            end_time = now.strftime('%Y-%m-%d')
        elif text == "近半年":
            begin_time = (now - timedelta(days=180)).strftime('%Y-%m-%d')
            end_time = now.strftime('%Y-%m-%d')
        elif text == "近1年":
            begin_time = (now - timedelta(days=365)).strftime('%Y-%m-%d')
            end_time = now.strftime('%Y-%m-%d')
        elif text == "近2年":
            begin_time = (now - timedelta(days=730)).strftime('%Y-%m-%d')
            end_time = now.strftime('%Y-%m-%d')
        elif text == "全部":
            begin_time = "2020-01-01"
            end_time = now.strftime('%Y-%m-%d')
        else:
            begin_time = (now - timedelta(days=180)).strftime('%Y-%m-%d')
            end_time = now.strftime('%Y-%m-%d')

        return begin_time, end_time

    def get_default_download_path(self):
        """获取默认下载路径"""
        download_dir = os.path.join(
            os.path.expanduser("~"),
            "Downloads",
            "EastMoneyReports"
        )
        os.makedirs(download_dir, exist_ok=True)
        return download_dir

    def on_industry_clicked(self, item, column):
        """行业点击事件"""
        data = item.data(0, Qt.UserRole)
        if not data:
            return

        if data.get("type") == "all":
            # 全部行业 - 不指定industry_code
            self.current_industry_code = None
            self.current_page = 1
            self.current_report_type = self.get_report_type()
            self.query_reports()
        elif data.get("type") == "industry":
            self.current_industry_code = data.get("code")
            self.current_page = 1
            self.current_report_type = self.get_report_type()
            self.query_reports()

    def on_type_changed(self):
        """研报类型改变"""
        self.current_report_type = self.get_report_type()
        self.current_page = 1
        self.query_reports()

    def on_search(self):
        """搜索按钮点击"""
        self.current_report_type = self.get_report_type()
        self.current_page = 1
        self.query_reports()

    def on_refresh(self):
        """刷新按钮点击"""
        self.query_reports()

    def on_select_download_path(self):
        """选择下载目录"""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "选择下载目录",
            self.download_path_input.text()
        )
        if dir_path:
            self.download_path_input.setText(dir_path)

    def query_reports(self):
        """查询研报"""
        self.status_label.setText("正在查询...")
        self.report_table.setRowCount(0)

        report_type = self.current_report_type
        industry_code = self.current_industry_code
        search_text = self.search_input.text().strip()
        page_no = self.current_page
        page_size = int(self.page_size_combo.currentText())

        # 获取时间范围
        begin_time, end_time = self.get_time_range()

        kwargs = {
            "report_type": report_type,
            "page_no": page_no,
            "page_size": page_size,
            "begin_time": begin_time,
            "end_time": end_time
        }

        # 只有指定了行业代码时才添加该参数
        if report_type == "industry" and industry_code:
            kwargs["industry_code"] = industry_code
        # industry_code 为 None 或空时，查询全部行业

        if search_text:
            if search_text.isdigit():
                kwargs["stock_code"] = search_text

        try:
            result = self.client.fetch_reports(**kwargs)

            if result and result.get("data"):
                self.current_reports = result["data"]
                # API返回 hits 或 TotalPage
                total = result.get("hits", 0)
                if total == 0:
                    total = len(result["data"])

                # 使用API返回的TotalPage或计算
                api_total_pages = result.get("TotalPage", 0)
                if api_total_pages > 0:
                    self.total_pages = api_total_pages
                else:
                    self.total_pages = max(1, (total + page_size - 1) // page_size)

                self.update_report_table()
                self.update_page_label()
                self.status_label.setText(f"找到 {total} 条研报")
            else:
                self.current_reports = []
                self.report_table.setRowCount(0)
                self.total_pages = 1
                self.update_page_label()
                self.status_label.setText("未找到研报")

        except Exception as e:
            self.status_label.setText(f"查询失败: {str(e)}")

    def update_report_table(self):
        """更新研报表格"""
        self.report_table.setRowCount(len(self.current_reports))

        for row, report in enumerate(self.current_reports):
            # 确保研报类型信息存在
            report["_report_type"] = self.current_report_type

            # 获取唯一标识并检查保存的勾选状态
            report_id = self.get_report_id(report)
            is_checked = self._checked_reports.get(report_id, False)

            # 选择框
            checkbox = QTableWidgetItem()
            checkbox.setCheckState(Qt.Checked if is_checked else Qt.Unchecked)
            checkbox.setData(Qt.UserRole, report)
            self.report_table.setItem(row, 0, checkbox)
            
            # 标题
            title = report.get("title", "")
            title_item = QTableWidgetItem(title)
            title_item.setData(Qt.UserRole, report)
            title_item.setToolTip(title)
            self.report_table.setItem(row, 1, title_item)

            # 机构
            org_name = report.get("orgName", report.get("pubName", ""))
            org_item = QTableWidgetItem(org_name)
            self.report_table.setItem(row, 2, org_item)

            # 股票名称（优先显示名称，没有则显示代码）
            stock_name = report.get("stockName", "")
            if not stock_name:
                stock_name = report.get("stockCode", "")
            self.report_table.setItem(row, 3, QTableWidgetItem(stock_name))

            # 发布日期
            publish_date = report.get("publishDate", report.get("pubDate", ""))
            if publish_date:
                publish_date = publish_date[:10] if len(publish_date) > 10 else publish_date
            self.report_table.setItem(row, 4, QTableWidgetItem(publish_date))

            # 下载按钮
            download_btn = ModernButton("下载", primary=True)
            download_btn.setFixedWidth(70)
            download_btn.set_debounce_duration(1500)
            # 使用防抖点击
            download_btn.clicked.connect(lambda checked, r=row, btn=download_btn: (
                btn.setEnabled(False),
                QTimer.singleShot(1500, lambda: btn.setEnabled(True)),
                self.on_single_download(r)
            ))
            self.report_table.setCellWidget(row, 5, download_btn)

    def update_page_label(self):
        """更新分页标签"""
        total = self.total_pages
        current = self.current_page
        self.page_label.setText(f"第 {current}/{total} 页")

    def on_row_double_clicked(self, item):
        """双击行下载"""
        row = item.row()
        if row < len(self.current_reports):
            self.on_single_download(row)

    def on_single_download(self, row):
        """单个下载"""
        if row < len(self.current_reports):
            report = self.current_reports[row]
            self.download_report(report)

    def on_cell_clicked(self, row, column):
        """单元格点击事件 - 切换复选框"""
        if column == 0 and row < len(self.current_reports):
            item = self.report_table.item(row, 0)
            if item:
                # 切换复选框状态
                if item.checkState() == Qt.Checked:
                    item.setCheckState(Qt.Unchecked)
                else:
                    item.setCheckState(Qt.Checked)

    def on_item_changed(self, item):
        """表格项变化时更新待下载列表"""
        # 防止重复处理
        if self._processing_checkbox:
            return
        self._processing_checkbox = True

        try:
            self.process_checkbox_change(item)
        finally:
            self._processing_checkbox = False

    def get_report_id(self, report):
        """获取研报唯一标识"""
        # 优先使用 infoCode，其次使用 title + publishDate 组合
        info_code = report.get("info_code", "")
        if info_code:
            return info_code
        title = report.get("title", "")
        publish_date = report.get("publishDate", "")[:10]
        return f"{title}_{publish_date}"

    def process_checkbox_change(self, item):
        """处理复选框状态变化"""
        # 忽略还没有创建 download_list_btn 的情况
        if not hasattr(self, 'download_list_btn'):
            return

        # 获取item关联的研报数据
        report = item.data(Qt.UserRole)
        if not report:
            return

        # 获取唯一标识
        report_id = self.get_report_id(report)
        if not report_id:
            return

        # 检查这个研报是否在当前显示的列表中
        # 如果不在，说明是页面切换时旧数据触发的信号，直接忽略
        current_ids = [self.get_report_id(r) for r in self.current_reports]
        if report_id not in current_ids:
            return

        # 保存勾选状态
        is_checked = item.checkState() == Qt.Checked
        self._checked_reports[report_id] = is_checked

        # 确保研报类型存在
        if "_report_type" not in report:
            report["_report_type"] = self.current_report_type

        if is_checked:
            # 勾选：添加到待下载列表（去重）
            existing_ids = [self.get_report_id(r) for r in self.download_list]
            if report_id not in existing_ids:
                self.download_list.append(report)
        else:
            # 取消勾选：从待下载列表移除
            for i, r in enumerate(self.download_list):
                if self.get_report_id(r) == report_id:
                    self.download_list.pop(i)
                    break

        # 更新待下载数量显示
        self.update_download_list_count()

    def on_item_check_changed(self, item):
        """复选框状态变化时更新待下载列表"""
        if not item:
            return

        # 忽略还没有创建 download_list_btn 的情况（表格初始化时）
        if not hasattr(self, 'download_list_btn'):
            return

        # 只处理第0列（选择框列）
        try:
            col = item.column()
        except:
            col = 0
        if col != 0:
            return

        report = item.data(Qt.UserRole)
        if not report:
            return

        # 确保研报类型存在
        if "_report_type" not in report:
            report["_report_type"] = self.current_report_type

        info_code = report.get("info_code")
        if not info_code:
            return

        # 检查是否已在列表中
        existing_index = None
        for i, r in enumerate(self.download_list):
            if r.get("info_code") == info_code:
                existing_index = i
                break

        if item.checkState() == Qt.Checked:
            # 勾选：添加到待下载列表（去重）
            if existing_index is None:
                self.download_list.append(report)
        else:
            # 取消勾选：从待下载列表移除
            if existing_index is not None:
                self.download_list.pop(existing_index)

        # 更新待下载数量显示
        self.update_download_list_count()

    def update_download_list_count(self):
        """更新待下载数量显示"""
        count = len(self.download_list)
        if hasattr(self, 'download_list_btn'):
            if count > 0:
                self.download_list_btn.setText(f"📥 待下载({count})")
                self.download_list_btn.setStyleSheet(f"""
                    QPushButton {{
                        color: {Colors.PRIMARY};
                        font-weight: bold;
                        background-color: transparent;
                        border: none;
                        padding: 4px 10px;
                        text-align: left;
                    }}
                    QPushButton:hover {{
                        color: {Colors.PRIMARY};
                        background-color: #F1F5F9;
                        border-radius: 4px;
                    }}
                """)
            else:
                self.download_list_btn.setText("📥 待下载(0)")
                self.download_list_btn.setStyleSheet(f"""
                    QPushButton {{
                        color: {Colors.TEXT_SECONDARY};
                        background-color: transparent;
                        border: none;
                        padding: 4px 10px;
                        text-align: left;
                    }}
                    QPushButton:hover {{
                        color: {Colors.PRIMARY};
                        background-color: #F1F5F9;
                        border-radius: 4px;
                    }}
                """)

    def show_download_list_panel(self):
        """显示待下载列表面板"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QTextBrowser

        # 如果面板已存在，先关闭
        if hasattr(self, 'download_list_dialog') and self.download_list_dialog:
            self.download_list_dialog.close()

        dialog = QDialog(self)
        dialog.setWindowTitle("📥 待下载列表")
        dialog.setFixedSize(500, 400)
        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {Colors.BG_MAIN};
            }}
        """)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # 标题栏
        header = QHBoxLayout()
        title_label = QLabel(f"已选择 {len(self.download_list)} 份研报")
        title_label.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {Colors.TEXT_MAIN};")
        header.addWidget(title_label)
        header.addStretch()
        layout.addLayout(header)

        # 研报列表
        list_widget = QListWidget()
        list_widget.setStyleSheet(f"""
            QListWidget {{
                background-color: white;
                border: 1px solid {Colors.BORDER};
                border-radius: 6px;
                padding: 5px;
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {Colors.BORDER};
            }}
            QListWidget::item:hover {{
                background-color: #F1F5F9;
            }}
        """)

        for i, report in enumerate(self.download_list, 1):
            title = report.get("title", "无标题")[:40]
            org = report.get("orgName", report.get("pubName", ""))
            date = report.get("publishDate", "")[:10]
            report_type = report.get("_report_type", "")
            type_names = {
                "industry": "行业",
                "stock": "个股",
                "strategy": "策略",
                "macro": "宏观",
                "morning": "晨报"
            }
            type_name = type_names.get(report_type, report_type)

            item_text = f"{i}. [{type_name}] {title}\n   {org} | {date}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, report)
            list_widget.addItem(item)

        layout.addWidget(list_widget)

        # 按钮栏
        button_layout = QHBoxLayout()

        # 清空按钮
        clear_btn = ModernButton("清空")
        clear_btn.setFixedWidth(80)
        clear_btn.clicked.connect(lambda: self.clear_download_list(list_widget, dialog))
        button_layout.addWidget(clear_btn)

        button_layout.addStretch()

        # 批量下载按钮
        download_btn = ModernButton("⬇ 批量下载", primary=True)
        download_btn.setFixedWidth(120)
        download_btn.set_debounce_duration(1500)
        download_btn.clicked.connect(lambda: self.batch_download_from_list(dialog))
        button_layout.addWidget(download_btn)

        layout.addLayout(button_layout)

        # 保持对话框引用
        self.download_list_dialog = dialog
        dialog.exec()

    def clear_download_list(self, list_widget=None, dialog=None):
        """清空待下载列表"""
        if not self.download_list:
            return

        # 清除表格中的所有勾选状态
        for row in range(self.report_table.rowCount()):
            item = self.report_table.item(row, 0)
            if item:
                item.setCheckState(Qt.Unchecked)

        # 清空列表
        self.download_list.clear()

        # 更新显示
        self.update_download_list_count()

        # 关闭对话框
        if dialog:
            dialog.close()

    def batch_download_from_list(self, dialog=None):
        """从待下载列表批量下载"""
        if not self.download_list:
            QMessageBox.information(self, "提示", "待下载列表为空")
            return

        # 关闭对话框
        if dialog:
            dialog.close()

        # 执行批量下载
        count = len(self.download_list)
        self.status_label.setText(f"正在下载 {count} 个文件...")
        for i, report in enumerate(self.download_list, 1):
            self.download_report(report)
            self.download_status_label.setText(f"已添加 {i}/{count}")

        # 下载完成后清空列表（可选）
        # self.download_list.clear()
        # self.update_download_list_count()

    def on_select_all(self):
        """全选"""
        for row in range(self.report_table.rowCount()):
            self.report_table.item(row, 0).setCheckState(Qt.Checked)

    def on_deselect_all(self):
        """取消全选"""
        for row in range(self.report_table.rowCount()):
            self.report_table.item(row, 0).setCheckState(Qt.Unchecked)

    def on_batch_download(self):
        """批量下载选中"""
        selected_reports = []

        for row in range(self.report_table.rowCount()):
            item = self.report_table.item(row, 0)
            if item and item.checkState() == Qt.Checked:
                report = item.data(Qt.UserRole)
                if report:
                    # 确保有研报类型
                    if "_report_type" not in report:
                        report["_report_type"] = self.current_report_type
                    selected_reports.append(report)

        if not selected_reports:
            QMessageBox.information(self, "提示", "请先选择要下载的研报")
            return

        # 批量下载
        count = len(selected_reports)
        self.status_label.setText(f"正在下载 {count} 个文件...")
        for i, report in enumerate(selected_reports, 1):
            self.download_report(report)
            self.download_status_label.setText(f"已添加 {i}/{count}")

    def download_report(self, report):
        """下载研报"""
        download_dir = self.download_path_input.text()

        if not download_dir:
            QMessageBox.warning(self, "警告", "请设置下载目录")
            return

        title = report.get("title", "")[:30]
        self.download_manager.add_task(report, download_dir)
        self.status_label.setText(f"⏳ 正在下载: {title}...")

    def on_download_progress(self, filename, current, total):
        """下载进度更新"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.download_status_label.setText(f"↓ {filename}")

    def on_download_finished(self, filename, success):
        """下载完成"""
        self.progress_bar.setVisible(False)

        if success:
            self.status_label.setText(f"✅ 下载完成: {filename}")
            self.download_status_label.setText("")
            # 不再自动打开文件夹
        else:
            self.status_label.setText(f"❌ 下载失败: {filename}")

    def open_download_folder(self, filename):
        """打开下载文件夹"""
        try:
            download_dir = self.download_path_input.text()
            report_type = self.current_report_type
            folder = os.path.join(download_dir, report_type)
            folder = os.path.abspath(folder)

            if os.name == 'nt':
                os.startfile(folder)
            elif os.name == 'posix':
                import subprocess
                subprocess.run(['open', folder])
        except:
            pass

    # 分页相关方法
    def on_first_page(self):
        self.current_page = 1
        self.query_reports()

    def on_prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.query_reports()

    def on_next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.query_reports()

    def on_last_page(self):
        self.current_page = self.total_pages
        self.query_reports()

    def on_page_size_changed(self, size):
        self.current_page = 1
        self.query_reports()
