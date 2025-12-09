import json
import os
import time

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from components.image_handler import ImageHandler



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
            with open('./source/tabs-config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)

            if self.tab_name in config:
                return config[self.tab_name].get('scroll', [])
            return []
        except Exception as e:
            print(f"读取时间戳数据出错: {e}")
            return []

    # 修改 guitartab_manager.py 中的 FullScreenImageWindow 类的 save_timestamp_to_config 方法

    def save_timestamp_to_config(self, timestamp_time, position, is_home=False):
        """保存时间戳到配置文件"""
        try:
            # 读取现有配置
            with open('source/tabs-config.json', 'r', encoding='utf-8') as f:
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
                with open('source/tabs-config.json', 'w', encoding='utf-8') as f:
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

