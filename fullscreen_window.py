import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk
import json
import os
import time

from components.image_handler import ImageHandler


class FullScreenImageWindow:
    def __init__(self, parent=None):
        self.parent = parent
        self.root = tk.Toplevel()
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')
        # 初始化变量
        self.combined_image_path = ""
        self.is_auto_scrolling = False
        self.auto_scroll_after_id = None
        self.start_time = 0
        self.tab_name = ""
        self.smooth_step = 0.002  # 平滑滚动步长（原0.02的1/10）
        self.smooth_refresh_ms = 16  # 约60帧/秒（更流畅的刷新率）
        self.target_view_fraction = 0.0  # 目标滚动位置（用于平滑插值）

        self.setup_ui()
        # ========== 新增：延迟加载图片（关键，触发load_image） ==========
        self.root.after(100, self.delayed_load_image)

    def delayed_load_image(self):
        """延迟加载图片，确保组件尺寸初始化完成"""
        # 优先获取parent的current_tab，无则用测试图片
        if hasattr(self.parent, 'current_tab') and self.parent.current_tab:
            self.tab_name = self.parent.current_tab
        else:
            self.tab_name = "test"  # 兜底tab_name
            # 强制使用本地测试图片（替换为你的图片路径！！！）
            self.combined_image_path = "C:/test.jpg"  # 替换成你电脑上的真实图片路径（绝对路径）
            self.image_label.configure(
                bg='black',
                text='使用测试图片路径，请检查parent.current_tab',
                fg='white'
            )
            print("警告：parent.current_tab为空，使用测试图片路径")

        # 强制加载（无论tab_name是否有效）
        self.load_image(self.tab_name)
    def setup_ui(self):
        # 创建主框架
        self.main_frame = tk.Frame(self.root, bg='black')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 创建画布用于滚动显示图像
        self.canvas = tk.Canvas(self.main_frame, bg='black', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='black')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # 图像标签
        self.image_label = tk.Label(self.scrollable_frame, bg='black')
        self.image_label.pack()

        # 控制按钮框架
        self.button_frame = tk.Frame(self.root, bg='white')
        self.button_frame.place(relx=0.12, rely=0.02, anchor='ne')

        # 添加时间戳按钮
        self.add_timestamp_btn = tk.Button(
            self.button_frame,
            text="● 添加时间戳",
            bg='white',
            fg='black',
            command=self.add_timestamp
        )
        self.add_timestamp_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # 自动滚动按钮
        self.auto_scroll_btn = tk.Button(
            self.button_frame,
            text="▶ 自动滚动",
            bg='white',
            fg='black',
            command=self.toggle_auto_scroll
        )
        self.auto_scroll_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # 绑定事件
        self.root.bind('<Escape>', lambda e: self.exit_fullscreen())
        self.root.bind('<Double-Button-1>', lambda e: self.exit_fullscreen())
        self.canvas.bind('<MouseWheel>', self.on_mousewheel)
        self.root.bind('<Configure>', self.on_resize)
        # ========== 修复：避免事件绑定冲突，改用after刷新 ==========
        self.canvas.bind('<MouseWheel>', lambda e: [self.on_mousewheel(e), self.root.after(10, self.draw_image_markers())])
        # 新增：画布滚动后强制刷新标记
        self.canvas.bind('<B1-Motion>', lambda e: self.root.after(10, self.draw_image_markers()))
        # ========== 强制刷新UI ==========
        self.root.update_idletasks()  # 强制渲染组件
        self.canvas.update_idletasks()
        self.image_label.update_idletasks()

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_resize(self, event):
        # 优化：仅当窗口宽度变化且图片已加载时才重新加载
        if (hasattr(self,
                    'last_width') and self.last_width == self.canvas.winfo_width()) or not self.combined_image_path:
            return
        self.last_width = self.canvas.winfo_width()
        if hasattr(self.parent, 'current_tab') and self.parent.current_tab and self.combined_image_path:
            if os.path.exists(self.combined_image_path):
                self.load_image(self.tab_name)
                # ========== 新增 ==========
                self.root.after(100, self.draw_image_markers)
                # ========== 新增结束 ==========
    def load_image(self, tab_name):
        self.tab_name = tab_name
        try:
            # 这里需要调用 ImageHandler.create_combined_image
            self.combined_image_path = rf"C:\Users\31118\PycharmProjects\guitar\source\晴天\combined_fullscreen.png"

            if self.combined_image_path and os.path.exists(self.combined_image_path):
                image = Image.open(self.combined_image_path)
                # 缩放到窗口宽度（优化：使用更平滑的缩放算法）
                width = self.root.winfo_screenwidth()
                ratio = width / image.width
                new_height = int(image.height * ratio)
                resized_image = image.resize((width, new_height), Image.Resampling.LANCZOS if hasattr(Image.Resampling,
                                                                                                      'LANCZOS') else Image.ANTIALIAS)

                self.photo = ImageTk.PhotoImage(resized_image)
                self.image_label.configure(
                    image=self.photo,
                    bg='black',
                    text='',  # 清空文字
                    fg='white'
                )
                self.image_label.image = self.photo  # 保持引用
                # 初始化滚动位置
                self.canvas.yview_moveto(0.0)
                self.root.after(100, self.draw_image_markers)  # 延迟绘制确保尺寸就绪
            else:
                # 路径无效时显示提示文字
                self.image_label.configure(
                    image='',  # 清空图片
                    bg='black',
                    text=f"图片路径无效:\n{self.combined_image_path}",
                    fg='white',
                    font=('Arial', 12)
                )
                print(f"错误：图片路径不存在或为空")
        except Exception as e:
            # 加载异常时显示错误信息
            self.image_label.configure(
                image='',
                bg='black',
                text=f"图片加载失败:\n{str(e)}",
                fg='white',
                font=('Arial', 12)
            )
            print(f"加载异常详情: {e}")

    def add_timestamp(self):
        # 获取当前滚动位置（优化：更精确的像素位置计算）
        view_pos = self.canvas.yview()
        content_height = self.scrollable_frame.winfo_height()
        canvas_height = self.canvas.winfo_height()
        current_pos = view_pos[0] * (content_height - canvas_height) if (content_height - canvas_height) > 0 else 0

        # 弹出对话框获取时间输入
        time_text = simpledialog.askstring("添加时间戳", "请输入时间 (格式: A分BC秒 例如: 1分23秒)")
        if time_text:
            try:
                total_seconds = self.parse_time_input(time_text)
                if total_seconds is not None:
                    is_home = messagebox.askyesno("设置起始点", "是否设为起始点?")
                    self.save_timestamp_to_config(total_seconds, current_pos, is_home)
                else:
                    messagebox.showwarning("错误", "时间格式不正确，请使用格式如: 1分23秒")
            except Exception as e:
                messagebox.showwarning("错误", f"时间解析出错: {str(e)}")

    def parse_time_input(self, time_str):
        # 修复：原正则表达式错误，匹配"1分23秒"应该用正确的正则
        import re
        # 正确匹配 "1分23秒" 格式：匹配 数字+分+数字+秒
        pattern = r'(\d+)分(\d+)秒'
        match = re.match(pattern, time_str.strip())
        if match:
            minutes = int(match.group(1))
            seconds = int(match.group(2))
            # 优化：原逻辑的 thirds 是毫秒？修正为 分*60 + 秒
            return minutes * 60 + seconds
        # 兼容纯数字格式（秒）
        if time_str.isdigit():
            return int(time_str)
        return None

    def save_timestamp_to_config(self, timestamp_time, position, is_home=False):
        # 保存时间戳到配置文件
        try:
            # 优化：确保目录存在
            os.makedirs('source', exist_ok=True)
            # 优化：处理文件不存在的情况
            if not os.path.exists('source/tabs-config.json'):
                config = {}
            else:
                with open('source/tabs-config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)

            if self.tab_name not in config:
                config[self.tab_name] = {}
            if 'scroll' not in config[self.tab_name]:
                config[self.tab_name]['scroll'] = []

            new_point = {
                'time': round(timestamp_time, 2),
                'position': int(position),  # 优化：四舍五入减少精度问题
                'home': is_home
            }
            # 优化：去重（避免重复添加相同时间戳）
            config[self.tab_name]['scroll'] = [p for p in config[self.tab_name]['scroll'] if
                                               not (abs(p['time'] - new_point['time']) < 0.1)]
            config[self.tab_name]['scroll'].append(new_point)
            config[self.tab_name]['scroll'].sort(key=lambda x: x['time'])

            with open('source/tabs-config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        # ========== 修复：缩进错误，移到try块末尾 ==========
        except Exception as e:
            print(f"保存时间戳到配置文件出错: {e}")
            messagebox.showerror("错误", f"保存失败：{str(e)}")
        # 无论是否报错，都刷新标记（缩进外移）
        self.draw_image_markers()  # 新增时间戳后刷新标记
    def get_current_scroll_data(self):
        # 获取当前谱子的时间戳数据
        try:
            if not os.path.exists('source/tabs-config.json'):
                return []
            with open('source/tabs-config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)

            if self.tab_name in config:
                return config[self.tab_name].get('scroll', [])
            return []
        except Exception as e:
            print(f"读取时间戳数据出错: {e}")
            return []

    def get_next_timestamp(self, scroll_data, current_time):
        """
        找到当前时间之后紧邻的下一个时间戳（含home属性）
        返回：(next_time, next_pos, next_home) 或 None
        """
        # 筛选所有当前时间之后的时间戳
        next_timestamps = [
            (item['time'], item['position'], item['home'])
            for item in scroll_data
            if item['time'] > current_time - 0.1  # 0.1秒容差
        ]
        if next_timestamps:
            # 按时间排序，取最近的一个（紧邻的下一个）
            next_timestamps.sort(key=lambda x: x[0])
            return next_timestamps[0]
        return None

    def draw_image_markers(self):
        """直接在图片画布上绘制时间戳标记（叠加式，不遮挡图片）"""
        # 清空原有标记（只删除marker标签，不影响图片）
        self.canvas.delete("image_marker")
        if not self.combined_image_path or not os.path.exists(self.combined_image_path):
            return

        scroll_data = self.get_current_scroll_data()
        if not scroll_data:
            return

        # 获取关键尺寸
        # 1. 图片缩放后的尺寸（加兜底）
        scaled_width = self.image_label.winfo_width() or self.root.winfo_screenwidth()
        scaled_height = self.image_label.winfo_height() or self.root.winfo_screenheight()
        if scaled_height == 0:
            return
        # 2. 画布滚动偏移（关键：计算标记的绝对坐标）
        canvas_y = self.canvas.canvasy(0)  # 只需要y偏移，x固定在图片左侧
        # 3. 原始图片尺寸
        try:
            original_image = Image.open(self.combined_image_path)
            original_height = original_image.height
            scale_ratio = scaled_height / original_height  # 缩放比例
        except Exception as e:
            print(f"计算缩放比例失败：{e}")
            return

        # 自定义x坐标（图片左侧20px，固定值，无需抵消x偏移）
        marker_x = 20
        # 遍历时间戳绘制标记
        for item in scroll_data:
            # 计算标记的绝对y坐标（抵消滚动偏移）
            original_y = item['position']
            scaled_y = (original_y * scale_ratio) - canvas_y
            # 放宽可视区域判断（±50px，避免轻微偏移就不显示）
            if -50 <= scaled_y <= self.canvas.winfo_height() + 50:
                # 绘制标记：home=true红色实心圆，false白色空心圆
                if item['home']:
                    self.canvas.create_oval(
                        marker_x - 4, scaled_y - 4, marker_x + 4, scaled_y + 4,
                        fill='red', outline='red', tags='image_marker'
                    )
                else:
                    self.canvas.create_oval(
                        marker_x - 4, scaled_y - 4, marker_x + 4, scaled_y + 4,
                        fill='', outline='white', width=2, tags='image_marker'
                    )
        # 确保标记在最上层
        self.canvas.tag_raise("image_marker")
    def toggle_auto_scroll(self):
        if self.is_auto_scrolling:
            self.stop_auto_scroll()
        else:
            self.start_auto_scroll()

    def start_auto_scroll(self):
        self.is_auto_scrolling = True
        self.start_time = time.time()
        self.target_view_fraction = self.canvas.yview()[0]  # 初始化目标位置
        self.auto_scroll_btn.configure(text="⏹ 停止滚动", bg='red')
        self.auto_scroll_step()

    def stop_auto_scroll(self):
        self.is_auto_scrolling = False
        if self.auto_scroll_after_id:
            self.root.after_cancel(self.auto_scroll_after_id)
        self.auto_scroll_btn.configure(text="▶ 自动滚动", bg='blue')

    def auto_scroll_step(self):
        if not self.is_auto_scrolling:
            return

        elapsed_time = time.time() - self.start_time
        scroll_data = self.get_current_scroll_data()

        if not scroll_data:
            # 优化：平滑默认滚动（小步长）
            current_fraction = self.canvas.yview()[0]
            # 计算目标位置（缓慢增加）
            self.target_view_fraction = min(1.0, current_fraction + self.smooth_step)
            # 平滑插值到目标位置
            self.smooth_scroll_to(self.target_view_fraction)

            # 检查是否到底
            if self.canvas.yview()[1] >= 0.99:
                self.stop_auto_scroll()
                return
        else:
            # 核心：只找紧邻当前时间的下一个时间戳
            next_ts = self.get_next_timestamp(scroll_data, elapsed_time)
            max_y = self.scrollable_frame.winfo_height() - self.canvas.winfo_height()
            max_y = max_y if max_y > 0 else 1  # 避免除以0

            if next_ts:
                next_time, next_pos, next_home = next_ts

                # 直接判断下一个时间戳的home是否为true
                if next_home:
                    # 下一个是home=true：未到时间则暂停，到时间则跳转
                    if elapsed_time >= next_time - 0.02:
                        # 到点：直接跳转到该位置
                        target_fraction = next_pos / max_y
                        self.canvas.yview_moveto(max(0.0, min(1.0, target_fraction)))
                    else:
                        # 未到点：暂停滚动（固定当前位置）
                        current_fraction = self.canvas.yview()[0]
                        self.canvas.yview_moveto(current_fraction)
                else:
                    # 下一个是home=false：正常平滑滚动
                    target_position = self.calculate_position_by_time(elapsed_time, scroll_data)
                    target_fraction = target_position / max_y
                    self.smooth_scroll_to(max(0.0, min(1.0, target_fraction)))
            else:
                return
            #     # 无后续时间戳：继续默认滚动到底
            #     current_fraction = self.canvas.yview()[0]
            #     self.target_view_fraction = min(1.0, current_fraction + self.smooth_step)
            #     self.smooth_scroll_to(self.target_view_fraction)
            #
            # # 检查是否完成滚动
            # if elapsed_time > scroll_data[-1]['time'] and self.canvas.yview()[1] >= 0.99:
            #     self.stop_auto_scroll()
            #     return

        # 更高刷新率的回调
        self.auto_scroll_after_id = self.root.after(self.smooth_refresh_ms, self.auto_scroll_step)

    def smooth_scroll_to(self, target_fraction):
        """平滑滚动到目标视图比例（插值过渡）"""
        current_fraction = self.canvas.yview()[0]
        # 计算差值（小步长逼近目标）
        delta = target_fraction - current_fraction
        if abs(delta) < self.smooth_step / 2:
            # 差值足够小时直接到位
            self.canvas.yview_moveto(target_fraction)
        else:
            # 按步长插值
            step = self.smooth_step if delta > 0 else -self.smooth_step
            new_fraction = current_fraction + step
            # 确保不超过边界
            new_fraction = max(0.0, min(1.0, new_fraction))
            self.canvas.yview_moveto(new_fraction)

    def calculate_position_by_time(self, current_time, scroll_data):
        """优化：增加插值平滑度"""
        if not scroll_data:
            return 0

        if current_time <= scroll_data[0]['time']:
            return scroll_data[0]['position']

        if current_time >= scroll_data[-1]['time']:
            return scroll_data[-1]['position']

        for i in range(len(scroll_data) - 1):
            prev = scroll_data[i]
            next_ = scroll_data[i + 1]
            if prev['time'] <= current_time <= next_['time']:
                # 优化：使用线性插值，增加浮点精度
                t_range = next_['time'] - prev['time']
                if t_range == 0:
                    return prev['position']
                ratio = (current_time - prev['time']) / t_range
                # 平滑插值（增加小数精度）
                target_position = prev['position'] + (next_['position'] - prev['position']) * ratio
                return round(target_position, 2)

        return scroll_data[-1]['position']

    def exit_fullscreen(self):
        self.stop_auto_scroll()
        # 清理临时文件（优化：增加异常处理）
        if self.combined_image_path and os.path.exists(self.combined_image_path):
            try:
                # 仅删除临时文件（避免删除源文件）
                if 'temp' in self.combined_image_path.lower() or 'tmp' in self.combined_image_path.lower():
                    os.remove(self.combined_image_path)
            except Exception as e:
                print(f"清理临时文件失败: {e}")
        self.root.destroy()