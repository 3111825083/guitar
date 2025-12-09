# guitar_app.py
import sys
import json
import os
import time

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from image_handler import ImageHandler


class GuitarTabManager:
    """吉他谱管理器"""

    def __init__(self, config_file='tabs-config.json'):
        self.config_file = config_file
        self.tabs_data = {}
        self.load_config()

    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.tabs_data = json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {e}")

    def get_all_tabs(self):
        """获取所有吉他谱列表"""
        return self.tabs_data

    def get_tab_detail(self, tab_name):
        """获取指定吉他谱详情"""
        return self.tabs_data.get(tab_name, {})

    def search_tabs(self, keyword):
        """搜索吉他谱"""
        result = {}
        keyword = keyword.lower()
        for name, info in self.tabs_data.items():
            if (keyword in name.lower() or
                    keyword in info.get('singer', '').lower() or
                    keyword in info.get('type', '').lower()):
                result[name] = info
        return result
    def add_tab(self, tab_name, tab_info):
        """添加新歌曲"""
        try:
            self.tabs_data[tab_name] = tab_info
            self.save_config()
            return True
        except Exception as e:
            print(f"添加歌曲失败: {e}")
            return False

    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.tabs_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.tab_manager = GuitarTabManager()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("吉他谱查看器")
        self.setGeometry(100, 100, 1200, 800)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # 创建左侧列表面板
        self.create_list_panel(main_layout)

        # 创建右侧详情面板
        self.create_detail_panel(main_layout)

        # 初始化列表
        self.refresh_tab_list()

    # 在 MainWindow 类的 create_list_panel 方法中添加添加歌曲按钮
    def create_list_panel(self, parent_layout):
        """创建左侧列表面板"""
        list_panel = QWidget()
        list_panel.setMaximumWidth(350)
        layout = QVBoxLayout(list_panel)

        # 搜索框
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索歌曲名/歌手/类型...")
        self.search_input.textChanged.connect(self.on_search_changed)

        # 添加歌曲按钮
        self.add_song_btn = QPushButton("+ 添加歌曲")
        self.add_song_btn.clicked.connect(self.add_new_song)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.add_song_btn)
        layout.addLayout(search_layout)

        # 列表
        self.tab_list_widget = QListWidget()
        self.tab_list_widget.itemClicked.connect(self.on_tab_selected)
        layout.addWidget(self.tab_list_widget)

        parent_layout.addWidget(list_panel)

    def add_new_song(self):
        """添加新歌曲"""
        # 创建添加歌曲对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("添加新歌曲")
        dialog.setModal(True)
        dialog.resize(400, 300)

        # 设置样式
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #333;
                font-size: 12px;
                background-color: white;
            }
            QLineEdit, QComboBox {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
                color: #333;
            }
            QDialogButtonBox {
                background-color: white;
            }
            QDialogButtonBox QPushButton {
                background-color: white;
                color: #333;
                border: 1px solid #ccc;
                padding: 6px 12px;
                border-radius: 4px;
                min-width: 60px;
            }
            QDialogButtonBox QPushButton:hover {
                background-color: #f0f0f0;
                border-color: #999;
            }
            QDialogButtonBox QPushButton:pressed {
                background-color: #e0e0e0;
            }
        """)

        # 创建布局
        layout = QVBoxLayout(dialog)

        # 表单布局
        form_layout = QFormLayout()

        # 输入字段
        song_name_input = QLineEdit()
        singer_input = QLineEdit()
        type_combo = QComboBox()
        type_combo.addItems(["弹唱", "指弹", "独奏", "合奏"])

        form_layout.addRow("歌曲名:", song_name_input)
        form_layout.addRow("歌手:", singer_input)
        form_layout.addRow("类型:", type_combo)

        layout.addLayout(form_layout)

        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        # 显示对话框
        if dialog.exec_() == QDialog.Accepted:
            song_name = song_name_input.text().strip()
            singer = singer_input.text().strip()
            song_type = type_combo.currentText()

            if song_name and singer:
                # 检查歌曲是否已存在
                existing_tabs = self.tab_manager.get_all_tabs()
                if song_name in existing_tabs:
                    QMessageBox.warning(self, "警告", f"歌曲 '{song_name}' 已存在！")
                    return

                # 创建新的歌曲信息
                new_song_info = {
                    "id": str(len(existing_tabs) + 1),
                    "singer": singer,
                    "type": song_type,
                    "view": "0",
                    "download": "0",
                    "cover": f"https://picsum.photos/seed/{song_name.replace(' ', '')}/300/200",
                    "scroll": [
                        {
                            "time": 0,
                            "position": 0
                        }
                    ]
                }

                # 添加到配置中
                if self.tab_manager.add_tab(song_name, new_song_info):
                    # 创建对应的文件夹
                    source_dir = f"source/{song_name}"
                    if not os.path.exists(source_dir):
                        os.makedirs(source_dir)

                    # 刷新列表
                    self.refresh_tab_list()
                    QMessageBox.information(self, "成功", f"歌曲 '{song_name}' 添加成功！")
                else:
                    QMessageBox.critical(self, "错误", "添加歌曲失败！")
            else:
                QMessageBox.warning(self, "警告", "歌曲名和歌手不能为空！")

    def upload_guitar_tabs(self):
        """上传吉他谱图片"""
        if not self.current_tab:
            QMessageBox.warning(self, "警告", "请先选择一首歌曲！")
            return

        # 获取当前选中的歌曲名
        tab_name = None
        for name, info in self.tab_manager.get_all_tabs().items():
            if info == self.current_tab:
                tab_name = name
                break

        if not tab_name:
            QMessageBox.warning(self, "警告", "无法确定当前歌曲！")
            return

        # 选择图片文件
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg)")
        file_dialog.setViewMode(QFileDialog.List)

        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()

            if selected_files:
                source_dir = f"source/{tab_name}"

                # 复制文件到对应目录
                success_count = 0
                for i, file_path in enumerate(selected_files):
                    try:
                        # 生成目标文件名（从第1页开始）
                        target_filename = f"{i + 1}.png"
                        target_path = os.path.join(source_dir, target_filename)

                        # 复制文件
                        from PIL import Image
                        img = Image.open(file_path)
                        img.save(target_path, 'PNG')
                        success_count += 1
                    except Exception as e:
                        print(f"复制文件 {file_path} 失败: {e}")

                if success_count > 0:
                    QMessageBox.information(self, "成功", f"成功上传 {success_count} 张吉他谱图片！")
                    # 重新加载当前歌曲的图片
                    if self.current_tab:
                        self.load_tab_image()
                else:
                    QMessageBox.warning(self, "警告", "没有成功上传任何图片！")

    def create_detail_panel(self, parent_layout):
        """创建右侧详情面板"""
        detail_panel = QWidget()
        layout = QVBoxLayout(detail_panel)

        # 标题区域
        title_layout = QHBoxLayout()
        self.title_label = QLabel("请选择吉他谱")
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()

        # 收藏按钮
        self.favorite_btn = QPushButton("★ 收藏")
        self.favorite_btn.clicked.connect(self.toggle_favorite)
        title_layout.addWidget(self.favorite_btn)
        layout.addLayout(title_layout)

        # 信息展示区域
        info_group = QGroupBox("基本信息")
        info_layout = QFormLayout()
        self.singer_label = QLabel()
        self.type_label = QLabel()
        self.view_label = QLabel()
        self.download_label = QLabel()
        info_layout.addRow("歌手:", self.singer_label)
        info_layout.addRow("类型:", self.type_label)
        info_layout.addRow("浏览量:", self.view_label)
        info_layout.addRow("下载量:", self.download_label)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # 图片展示区域
        self.image_scroll = QScrollArea()
        self.image_label = QLabel("请选择吉他谱查看内容")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(400, 600)
        # 添加鼠标双击事件
        self.image_label.mouseDoubleClickEvent = lambda event: self.toggle_fullscreen(event)
        self.image_scroll.setWidget(self.image_label)
        self.image_scroll.setWidgetResizable(True)
        layout.addWidget(self.image_scroll)

        # 控制按钮
        control_layout = QHBoxLayout()
        self.prev_btn = QPushButton("上一页")
        self.next_btn = QPushButton("下一页")
        self.page_label = QLabel("第 1 页")
        self.upload_btn = QPushButton("上传谱子")
        self.download_btn = QPushButton("下载")
        self.print_btn = QPushButton("打印")

        self.prev_btn.clicked.connect(self.prev_page)
        self.next_btn.clicked.connect(self.next_page)
        self.upload_btn.clicked.connect(self.upload_guitar_tabs)
        self.download_btn.clicked.connect(self.download_tab)
        self.print_btn.clicked.connect(self.print_tab)

        control_layout.addWidget(self.prev_btn)
        control_layout.addWidget(self.page_label)
        control_layout.addWidget(self.next_btn)
        control_layout.addStretch()
        control_layout.addWidget(self.upload_btn)
        control_layout.addWidget(self.download_btn)
        control_layout.addWidget(self.print_btn)
        layout.addLayout(control_layout)

        self.current_tab = None
        self.current_page = 1
        self.total_pages = 0
        # 添加全屏相关属性
        self.is_fullscreen = False
        self.normal_geometry = None
        parent_layout.addWidget(detail_panel)

    def refresh_tab_list(self):
        """刷新吉他谱列表"""
        self.tab_list_widget.clear()
        tabs = self.tab_manager.get_all_tabs()
        for name, info in tabs.items():
            item = QListWidgetItem(f"{name} - {info['singer']}")
            item.setData(Qt.UserRole, name)
            self.tab_list_widget.addItem(item)

    def on_search_changed(self, text):
        """搜索框内容改变时"""
        pass  # 实时搜索可在此实现

    def on_search_clicked(self):
        """点击搜索按钮"""
        keyword = self.search_input.text()
        if keyword:
            self.tab_list_widget.clear()
            results = self.tab_manager.search_tabs(keyword)
            for name, info in results.items():
                item = QListWidgetItem(f"{name} - {info['singer']}")
                item.setData(Qt.UserRole, name)
                self.tab_list_widget.addItem(item)
        else:
            self.refresh_tab_list()

    def on_tab_selected(self, item):
        """选择吉他谱"""
        tab_name = item.data(Qt.UserRole)
        self.current_tab = self.tab_manager.get_tab_detail(tab_name)
        self.current_page = 1
        self.load_tab_detail(tab_name)

    def load_tab_detail(self, tab_name):
        """加载吉他谱详情"""
        if not self.current_tab:
            return

        # 更新基本信息
        self.title_label.setText(f"{tab_name} - {self.current_tab.get('singer', '')}")
        self.singer_label.setText(self.current_tab.get('singer', ''))
        self.type_label.setText(self.current_tab.get('type', ''))
        self.view_label.setText(self.current_tab.get('view', ''))
        self.download_label.setText(self.current_tab.get('download', ''))

        # 加载第一页图片
        self.load_tab_image()

    def load_tab_image(self):
        """加载当前页图片"""
        if not self.current_tab:
            return

        tab_name = list(self.tab_manager.get_all_tabs().keys())[
            list(self.tab_manager.get_all_tabs().values()).index(self.current_tab)
        ]

        image_path = f"source/{tab_name}/{self.current_page}.png"
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)

            if not pixmap.isNull():
                # 根据是否全屏模式决定图片缩放方式
                if self.is_fullscreen:
                    # 全屏模式：等比缩放到屏幕宽度
                    screen_width = QApplication.primaryScreen().availableGeometry().width() - 40
                    scaled_pixmap = pixmap.scaledToWidth(screen_width, Qt.SmoothTransformation)
                else:
                    # 正常模式：等比缩放到图片展示区域宽度
                    display_width = self.image_scroll.viewport().width() - 20
                    scaled_pixmap = pixmap.scaledToWidth(display_width, Qt.SmoothTransformation)
                self.image_label.setPixmap(scaled_pixmap)
                # 调整标签大小以适应图片
                self.image_label.resize(scaled_pixmap.size())
                self.page_label.setText(f"第 {self.current_page} 页")
            else:
                self.image_label.setText("图片加载失败")
                self.image_label.resize(self.image_scroll.viewport().size())
        else:
            self.image_label.setText("未找到图片文件")
            self.image_label.resize(self.image_scroll.viewport().size())
    def prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_tab_image()

    def next_page(self):
        """下一页"""
        self.current_page += 1
        # 检查下一页是否存在
        tab_name = list(self.tab_manager.get_all_tabs().keys())[
            list(self.tab_manager.get_all_tabs().values()).index(self.current_tab)
        ]
        next_image_path = f"source/{tab_name}/{self.current_page}.png"
        if os.path.exists(next_image_path):
            self.load_tab_image()
        else:
            self.current_page -= 1  # 回退

    def toggle_favorite(self):
        """切换收藏状态"""
        # 实现收藏功能
        QMessageBox.information(self, "提示", "收藏功能已触发")

    def download_tab(self):
        """下载吉他谱"""
        if self.current_tab:
            QMessageBox.information(self, "下载", "开始下载选中的吉他谱...")
            # 实现下载逻辑

    def print_tab(self):
        """打印吉他谱"""
        if self.current_tab:
            QMessageBox.information(self, "打印", "开始打印选中的吉他谱...")
            # 实现打印逻辑

    # 在 MainWindow 类中添加以下方法
    def toggle_fullscreen(self, event):
        """切换全屏模式"""
        if not self.is_fullscreen:
            self.enter_fullscreen()
        else:
            self.exit_fullscreen()

    def enter_fullscreen(self):
        """进入全屏图片显示模式"""
        if not self.current_tab:
            return

        # 创建全屏图片窗口
        self.fullscreen_window = FullScreenImageWindow(self)
        self.fullscreen_window.showFullScreen()
        self.is_fullscreen = True

        # 加载合并后的完整图片
        tab_name = list(self.tab_manager.get_all_tabs().keys())[
            list(self.tab_manager.get_all_tabs().values()).index(self.current_tab)
        ]
        self.fullscreen_window.load_image(tab_name)

    def exit_fullscreen(self):
        """退出全屏模式"""
        if hasattr(self, 'fullscreen_window') and self.fullscreen_window:
            self.fullscreen_window.close()
            self.fullscreen_window = None
            self.is_fullscreen = False

    def load_fullscreen_image(self):
        """加载全屏图片"""
        pass

    def keyPressEvent(self, event):
        """处理按键事件"""
        if event.key() == Qt.Key_Escape and self.is_fullscreen:
            self.exit_fullscreen()
        else:
            super().keyPressEvent(event)


class FullScreenImageWindow(QMainWindow):
    """全屏图片显示窗口"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.combined_image_path = ""
        self.scroll_area = None
        self.scroll_content = None
        self.image_label = None
        # 自动滚动相关属性
        self.auto_scroll_timer = QTimer()
        self.auto_scroll_timer.timeout.connect(self.auto_scroll_step)
        self.is_auto_scrolling = False
        self.tab_name = ""  # 当前谱子名称
        self.start_time = 0  # 自动滚动开始时间
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("全屏查看")
        self.setStyleSheet("background-color: black;")

        # 创建中央widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; }")

        # 创建滚动内容部件
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background-color: black;")

        # 创建内容布局
        content_layout = QVBoxLayout(self.scroll_content)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # 图片标签
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.image_label)

        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)

        # 创建按钮容器(悬浮在右上角)
        button_container = QWidget()
        button_container.setStyleSheet("background-color: transparent;")
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(10, 10, 10, 10)

        # 添加时间戳按钮
        self.add_timestamp_btn = QPushButton("● 添加时间戳")
        self.add_timestamp_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 0, 0, 180);
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 220);
            }
        """)
        self.add_timestamp_btn.clicked.connect(self.add_timestamp)

        # 开始/停止自动滚动按钮
        self.auto_scroll_btn = QPushButton("▶ 自动滚动")
        self.auto_scroll_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 123, 255, 180);
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(0, 123, 255, 220);
            }
        """)
        self.auto_scroll_btn.clicked.connect(self.toggle_auto_scroll)

        button_layout.addWidget(self.add_timestamp_btn)
        button_layout.addWidget(self.auto_scroll_btn)
        button_layout.addStretch()

        # 将按钮容器添加到主布局
        main_layout.addWidget(button_container)

    def load_image(self, tab_name):
        """加载合并后的完整图片"""
        self.tab_name = tab_name  # 保存当前谱子名称
        try:
            # 创建合并图片
            self.combined_image_path = ImageHandler.create_combined_image(tab_name)

            if self.combined_image_path and os.path.exists(self.combined_image_path):
                pixmap = QPixmap(self.combined_image_path)
                if not pixmap.isNull():
                    # 获取窗口宽度
                    window_width = self.scroll_area.viewport().width()

                    # 等比缩放图片到窗口宽度
                    scaled_pixmap = pixmap.scaledToWidth(
                        window_width,
                        Qt.SmoothTransformation
                    )
                    self.image_label.setPixmap(scaled_pixmap)
                    # 调整标签大小
                    self.image_label.resize(scaled_pixmap.size())
                else:
                    self.image_label.setText("图片加载失败")
            else:
                self.image_label.setText("未找到图片文件")
        except Exception as e:
            print(f"加载全屏图片出错: {e}")
            self.image_label.setText("图片加载出错")

    def resizeEvent(self, event):
        """窗口大小改变时重新加载图片"""
        super().resizeEvent(event)
        # 重新加载当前图片以适应新的窗口大小
        if (hasattr(self.main_window, 'current_tab') and
                self.main_window.current_tab and
                self.combined_image_path):
            if os.path.exists(self.combined_image_path):
                pixmap = QPixmap(self.combined_image_path)
                if not pixmap.isNull():
                    window_width = self.scroll_area.viewport().width()
                    scaled_pixmap = pixmap.scaledToWidth(
                        window_width,
                        Qt.SmoothTransformation
                    )
                    self.image_label.setPixmap(scaled_pixmap)
                    self.image_label.resize(scaled_pixmap.size())

    def wheelEvent(self, event):
        """处理鼠标滚轮事件用于垂直滚动"""
        # 直接传递滚轮事件给滚动区域进行垂直滚动
        self.scroll_area.wheelEvent(event)

    def add_timestamp(self):
        """添加时间戳点并保存到配置文件"""
        # 获取当前滚动位置
        current_pos = self.scroll_area.verticalScrollBar().value()

        # 创建自定义对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("添加时间戳")
        dialog.setModal(True)
        dialog.resize(400, 200)

        # 设置对话框样式
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #333;
                font-size: 12px;
                background-color: white;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
                color: #333;
            }
            QCheckBox {
                color: #333;
                background-color: white;
            }
            QDialogButtonBox {
                background-color: white;
            }
            QDialogButtonBox QPushButton {
                background-color: white;
                color: #333;
                border: 1px solid #ccc;
                padding: 6px 12px;
                border-radius: 4px;
                min-width: 60px;
            }
            QDialogButtonBox QPushButton:hover {
                background-color: #f0f0f0;
                border-color: #999;
            }
            QDialogButtonBox QPushButton:pressed {
                background-color: #e0e0e0;
            }
        """)

        # 创建布局
        layout = QVBoxLayout(dialog)

        # 时间输入标签和文本框
        time_label = QLabel("请输入时间 (格式: A分BC秒 例如: 1分23秒 或 2分05秒):")
        time_input = QLineEdit()
        time_input.setPlaceholderText("例如: 1分23秒")

        # 是否为起始点复选框，默认不选中
        home_checkbox = QCheckBox("设为起始点")
        home_checkbox.setChecked(False)  # 默认不选中

        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        # 添加控件到布局
        layout.addWidget(time_label)
        layout.addWidget(time_input)
        layout.addWidget(home_checkbox)
        layout.addWidget(button_box)

        # 显示对话框并获取结果
        result = dialog.exec_()

        if result == QDialog.Accepted:
            time_text = time_input.text()
            is_home = home_checkbox.isChecked()  # 获取是否为起始点的选择

            if time_text:
                try:
                    # 解析时间输入
                    total_seconds = self.parse_time_input(time_text)
                    if total_seconds is not None:
                        # 保存到配置文件，同时传递是否为起始点的参数
                        self.save_timestamp_to_config(total_seconds, current_pos, is_home)
                        print(f"添加时间戳: 时间 {total_seconds}s, 位置 {current_pos}px, 起始点: {is_home}")
                    else:
                        QMessageBox.warning(self, "错误", "时间格式不正确，请使用格式如: 1分23秒")
                except Exception as e:
                    QMessageBox.warning(self, "错误", f"时间解析出错: {str(e)}")

    def parse_time_input(self, time_str):
        """解析'A分BC秒'格式的时间输入，返回总秒数"""
        import re

        # 匹配格式如: 1分23秒, 2分05秒, 3分5秒
        pattern = r'(\d+)(\d+)(\d+)'
        match = re.match(pattern, time_str.strip())

        if match:
            minutes = int(match.group(1))
            seconds = int(match.group(2))
            thirds = int(match.group(3))
            return minutes * 60 + seconds*10 + thirds
        return None

    def get_current_scroll_data(self):
        """获取当前谱子的时间戳数据"""
        try:
            with open('tabs-config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)

            if self.tab_name in config:
                return config[self.tab_name].get('scroll', [])
            return []
        except Exception as e:
            print(f"读取时间戳数据出错: {e}")
            return []

    # 修改 guitar_app.py 中的 FullScreenImageWindow 类的 save_timestamp_to_config 方法

    def save_timestamp_to_config(self, timestamp_time, position, is_home=False):
        """保存时间戳到配置文件"""
        try:
            # 读取现有配置
            with open('tabs-config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 添加新的时间戳点
            if self.tab_name in config:
                if 'scroll' not in config[self.tab_name]:
                    config[self.tab_name]['scroll'] = []

                # 添加新的时间戳点
                new_point = {
                    'time': round(timestamp_time, 2),
                    'position': position,
                    'home': is_home  # 添加是否为起始点的标识
                }
                config[self.tab_name]['scroll'].append(new_point)

                # 按时间排序
                config[self.tab_name]['scroll'].sort(key=lambda x: x['time'])

                # 保存回文件
                with open('tabs-config.json', 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"保存时间戳到配置文件出错: {e}")

    def toggle_auto_scroll(self):
        """切换自动滚动状态"""
        if self.is_auto_scrolling:
            self.stop_auto_scroll()
        else:
            self.start_auto_scroll()

    def start_auto_scroll(self):
        """开始自动滚动"""
        self.is_auto_scrolling = True
        self.start_time = time.time()
        self.auto_scroll_timer.start(50)  # 50ms间隔
        self.auto_scroll_btn.setText("⏹ 停止滚动")
        self.auto_scroll_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(220, 53, 69, 180);
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(220, 53, 69, 220);
            }
        """)

    def stop_auto_scroll(self):
        """停止自动滚动"""
        self.is_auto_scrolling = False
        self.auto_scroll_timer.stop()
        self.auto_scroll_btn.setText("▶ 自动滚动")
        self.auto_scroll_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 123, 255, 180);
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(0, 123, 255, 220);
            }
        """)

    def auto_scroll_step(self):
        """自动滚动一步（基于时间戳的非匀速滚动）"""
        if not self.is_auto_scrolling:
            return

        # 计算经过的时间
        elapsed_time = time.time() - self.start_time

        # 获取时间戳数据
        scroll_data = self.get_current_scroll_data()

        if not scroll_data:
            # 如果没有时间戳数据，使用默认滚动
            scrollbar = self.scroll_area.verticalScrollBar()
            current_value = scrollbar.value()
            maximum_value = scrollbar.maximum()

            # 如果已经到底部，停止滚动
            if current_value >= maximum_value:
                self.stop_auto_scroll()
                return

            # 默认滚动速度
            new_value = min(current_value + 2, maximum_value)
            scrollbar.setValue(new_value)
            return

        # 根据时间戳数据计算当前位置
        target_position = self.calculate_position_by_time(elapsed_time, scroll_data)

        # 查找紧接的下一个时间戳点
        next_point = None
        for point in scroll_data:
            if point['time'] > elapsed_time:
                next_point = point
                break
        # 如果下一个点是起始点，则暂停默认滚动，等待到达该时间点
        if next_point and next_point.get('home', False):
            # 检查是否已到达下一个起始点时间戳的时间点
            if elapsed_time >= next_point['time']:
                # 已到达时间点，执行跳转
                scrollbar = self.scroll_area.verticalScrollBar()
                scrollbar.setValue(int(next_point['position']))
        else:
            # 设置滚动位置
            scrollbar = self.scroll_area.verticalScrollBar()
            scrollbar.setValue(int(target_position))

        # 检查是否已完成所有滚动
        if elapsed_time > scroll_data[-1]['time']:
            max_position = scrollbar.maximum()
            if scrollbar.value() >= max_position - 10:  # 接近底部
                self.stop_auto_scroll()

    def calculate_position_by_time(self, current_time, scroll_data):
        """根据当前时间和时间戳数据计算目标位置"""
        if not scroll_data:
            return 0

        # 如果时间小于第一个点的时间
        if current_time <= scroll_data[0]['time']:
            return scroll_data[0]['position']

        # 如果时间大于最后一个点的时间
        if current_time >= scroll_data[-1]['time']:
            return scroll_data[-1]['position']

        # 找到当前时间所在的区间
        for i in range(len(scroll_data) - 1):
            if scroll_data[i]['time'] <= current_time <= scroll_data[i + 1]['time']:
                # 线性插值计算位置
                t1, pos1 = scroll_data[i]['time'], scroll_data[i]['position']
                t2, pos2 = scroll_data[i + 1]['time'], scroll_data[i + 1]['position']

                # 计算插值比例
                ratio = (current_time - t1) / (t2 - t1) if t2 != t1 else 0
                # 计算目标位置
                target_position = pos1 + (pos2 - pos1) * ratio
                return target_position

        # 默认返回最后一个点的位置
        return scroll_data[-1]['position']

    def keyPressEvent(self, event):
        """处理按键事件"""
        if event.key() == Qt.Key_Escape:
            if self.main_window:
                self.main_window.exit_fullscreen()
        else:
            super().keyPressEvent(event)

    def mouseDoubleClickEvent(self, event):
        """双击退出全屏"""
        if self.main_window:
            self.main_window.exit_fullscreen()

    def closeEvent(self, event):
        """窗口关闭时清理临时文件"""
        # 停止自动滚动
        if self.is_auto_scrolling:
            self.stop_auto_scroll()

        # 清理临时文件
        if self.combined_image_path and os.path.exists(self.combined_image_path):
            try:
                os.remove(self.combined_image_path)
            except:
                pass
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
