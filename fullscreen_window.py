import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk
import json
import os
import time
import re


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
        self.smooth_step = 0.002  # 平滑滚动步长
        self.smooth_refresh_ms = 10  # 约60帧/秒
        self.target_view_fraction = 0.0  # 目标滚动位置
        self.last_width = -1
        self.original_image_height = 0  # 原始图片高度
        self.scaled_image_height = 0  # 缩放后图片高度
        self.photo = None  # 图片对象（保留引用避免被回收）
        self.image_item_id = None  # Canvas中图片项的ID

        # ========== 核心新增：屏幕判断位置m（可自定义） ==========
        self.screen_marker_pos = 0.8  # 0-1之间，0=窗口顶部，1=窗口底部，0.5=中间
        self.marker_reach_threshold = 0.02  # 到达判断阈值（±2%）

        # ========== 拖动/点击修改相关变量 ==========
        self.marker_id_to_data = {}  # 标记ID → 对应时间戳数据的映射
        self.dragging_marker_id = None  # 当前正在拖动的标记ID
        self.drag_start_y = 0  # 拖动起始Y坐标

        # ========== 新增：段内滚动状态变量 ==========
        self.current_segment = None  # 当前滚动段：(start_time, end_time, start_pos, end_pos)
        self.segment_start_scroll_time = 0  # 当前段开始滚动的时间戳

        self.setup_ui()
        # 延迟加载图片（确保组件尺寸初始化完成）
        self.root.after(100, self.delayed_load_image)

    def delayed_load_image(self):
        """延迟加载图片，确保组件尺寸初始化完成"""
        self.tab_name = self.parent.current_tab_name
        self.load_image(self.tab_name)
        self.root.after(200, self.draw_image_markers)  # 加载后绘制标记

    def setup_ui(self):
        # 创建主框架
        self.main_frame = tk.Frame(self.root, bg='black')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 核心简化：单个Canvas同时显示图片+绘制标记
        self.canvas = tk.Canvas(self.main_frame, bg='black', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 控制按钮框架
        self.button_frame = tk.Frame(self.root, bg='white')
        self.button_frame.place(relx=0.2, rely=0.02, anchor='ne')

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

        # ========== 新增：m位置设置按钮 ==========
        self.set_m_pos_btn = tk.Button(
            self.button_frame,
            text=f"当前M位置：{self.screen_marker_pos * 100}%",
            bg='white',
            fg='black',
            command=self.set_screen_marker_pos
        )
        self.set_m_pos_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # 绑定事件
        self.root.bind('<Escape>', lambda e: self.exit_fullscreen())
        self.root.bind('<Double-Button-1>', lambda e: self.exit_fullscreen())
        self.canvas.bind('<MouseWheel>', self.on_mousewheel)
        self.root.bind('<Configure>', self.on_resize)

        # ========== 拖动/点击事件绑定 ==========
        self.canvas.bind('<Button-1>', self.on_canvas_click)  # 点击（修改时间/开始拖动）
        self.canvas.bind('<Button-3>', self.on_canvas_right_click)  # 右键修改时间
        self.canvas.bind('<B1-Motion>', self.on_marker_drag)  # 拖动标记
        self.canvas.bind('<ButtonRelease-1>', self.on_marker_release)  # 松开拖动

    def set_screen_marker_pos(self):
        """设置屏幕判断位置m"""
        current_percent = self.screen_marker_pos * 100
        new_percent = simpledialog.askinteger(
            "设置M位置",
            f"当前M位置：{current_percent}%\n请输入新位置（0-100，单位%）：",
            initialvalue=int(current_percent),
            minvalue=0,
            maxvalue=100
        )
        if new_percent is not None:
            self.screen_marker_pos = new_percent / 100.0
            self.set_m_pos_btn.config(text=f"当前M位置：{new_percent}%")
            messagebox.showinfo("成功", f"M位置已设置为{new_percent}%")


    def on_canvas_click(self, event):
        """左键点击：点击标记则开始拖动，空白处画测试标记"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        # 检查是否点击标记 → 开始拖动
        clicked_items = self.canvas.find_overlapping(x - 5, y - 5, x + 5, y + 5)
        for item_id in clicked_items:
            if item_id in self.marker_id_to_data:
                self.start_marker_drag(event, item_id)
                return

        # 空白处 → 绘制蓝色测试标记
        self.canvas.delete("click_marker")
        self.canvas.create_oval(
            x - 5, y - 5, x + 5, y + 5,
            fill='blue', outline='blue', tags='click_marker'
        )

    def on_canvas_right_click(self, event):
        """右键点击：仅处理标记的时间修改"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        # 检查是否点击标记 → 弹出修改时间对话框
        clicked_items = self.canvas.find_overlapping(x - 5, y - 5, x + 5, y + 5)
        for item_id in clicked_items:
            if item_id in self.marker_id_to_data:
                self.edit_marker_time(item_id)
                return

    def on_marker_drag(self, event):
        """拖动标记事件：实时更新标记位置"""
        if not self.dragging_marker_id:
            return
        # 转换为Canvas绝对坐标
        current_y = self.canvas.canvasy(event.y)
        # 计算拖动偏移量
        delta_y = current_y - self.drag_start_y
        # 获取标记当前位置并更新
        marker_coords = self.canvas.coords(self.dragging_marker_id)
        # 只修改Y坐标（X固定在左侧20px）
        new_y1 = marker_coords[1] + delta_y
        new_y2 = marker_coords[3] + delta_y
        new_y1 = max(4, min(new_y1, self.scaled_image_height - 4))
        new_y2 = max(8, min(new_y2, self.scaled_image_height))
        self.canvas.coords(self.dragging_marker_id, 16, new_y1, 24, new_y2)
        # 更新拖动起始Y（避免累计偏移）
        self.drag_start_y = current_y

    def on_marker_release(self, event):
        """松开标记事件：保存新位置到配置文件"""
        if not self.dragging_marker_id:
            return

        # 获取标记最终位置
        marker_coords = self.canvas.coords(self.dragging_marker_id)
        marker_center_y = (marker_coords[1] + marker_coords[3]) / 2

        # 从映射中获取对应的数据项
        data_item = self.marker_id_to_data.get(self.dragging_marker_id)
        if data_item:
            # 转换为原始图片的position（反缩放）
            scale_ratio = self.scaled_image_height / self.original_image_height if self.original_image_height > 0 else 1.0
            original_position = int(marker_center_y / scale_ratio)

            # 更新数据项的position
            data_item['position'] = original_position
            # 保存到配置文件
            self.save_updated_marker_data()

        # 重置拖动状态
        self.canvas.itemconfig(self.dragging_marker_id, outline='red' if data_item['home'] else 'white', width=2)
        self.dragging_marker_id = None
        self.drag_start_y = 0

    def edit_marker_time(self, marker_id):
        """修改标记的时间戳"""
        data_item = self.marker_id_to_data.get(marker_id)
        if not data_item:
            return

        # 格式化当前时间显示（例如：1分23秒）
        current_seconds = data_item['time']
        minutes = int(current_seconds // 60)
        seconds = int(current_seconds % 60)
        current_time_str = f"{minutes}分{seconds}秒"

        # 弹出修改对话框
        new_time_str = simpledialog.askstring(
            "修改时间戳",
            f"当前时间：{current_time_str}\n请输入新时间（格式：ABC，代表A分BC秒）",
            initialvalue=current_time_str
        )
        if not new_time_str:
            return

        # 解析新时间
        new_seconds = self.parse_time_input(new_time_str)
        if new_seconds is None:
            messagebox.showwarning("错误", "时间格式不正确，请使用格式如: 1分23秒")
            return

        # 更新数据项
        data_item['time'] = round(new_seconds, 2)
        # 保存到配置文件
        self.save_updated_marker_data()
        # 重新绘制标记
        self.draw_image_markers()
        messagebox.showinfo("成功", f"时间戳已修改为：{new_time_str}")

    def save_updated_marker_data(self):
        """保存修改后的标记数据到配置文件"""
        config_path = 'source/tabs-config.json'
        try:
            # 读取现有配置
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {}

            # 确保配置结构存在
            if self.tab_name not in config:
                config[self.tab_name] = {}
            if 'scroll' not in config[self.tab_name]:
                config[self.tab_name]['scroll'] = []

            # 替换为修改后的列表（去重+排序）
            updated_scroll_data = list(self.marker_id_to_data.values())
            updated_scroll_data = [p for p in updated_scroll_data if p]  # 过滤空值
            # 去重
            updated_scroll_data = [p for i, p in enumerate(updated_scroll_data) if
                                   not any(abs(p['time'] - q['time']) < 0.1 for q in updated_scroll_data[:i])]
            # 排序
            updated_scroll_data.sort(key=lambda x: x['time'])

            config[self.tab_name]['scroll'] = updated_scroll_data

            # 保存
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{str(e)}")

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_resize(self, event):
        # 仅当窗口宽度变化且图片已加载时才重新加载
        if (self.last_width == self.canvas.winfo_width()) or not self.combined_image_path:
            return
        self.last_width = self.canvas.winfo_width()
        if os.path.exists(self.combined_image_path):
            self.load_image(self.tab_name)
            self.root.after(100, self.draw_image_markers)

    def load_image(self, tab_name):
        """加载图片并显示在Canvas上（替代Label）"""
        self.tab_name = tab_name
        try:
            # 确定图片路径
            if not self.combined_image_path:
                self.combined_image_path = rf"source\{self.tab_name}\combined_fullscreen.png"

            if not os.path.exists(self.combined_image_path):
                return

            # 打开并缩放图片
            image = Image.open(self.combined_image_path)
            self.original_image_height = image.height
            width = self.canvas.winfo_width() or self.root.winfo_screenwidth()
            ratio = width / image.width
            new_height = int(image.height * ratio)
            self.scaled_image_height = new_height

            # 高质量缩放
            resized_image = image.resize((width, new_height), Image.Resampling.LANCZOS if hasattr(Image.Resampling,
                                                                                                  'LANCZOS') else Image.ANTIALIAS)
            self.photo = ImageTk.PhotoImage(resized_image)

            # 清除原有图片，绘制新图片
            if self.image_item_id:
                self.canvas.delete(self.image_item_id)
            self.image_item_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

            # 设置Canvas滚动区域（匹配图片尺寸）
            self.canvas.configure(scrollregion=(0, 0, width, new_height))
            # 初始化滚动位置
            self.canvas.yview_moveto(0.0)

        except Exception as e:
            return

    def add_timestamp(self):
        """添加时间戳（记录当前滚动位置）"""
        # 获取当前滚动位置（绝对坐标）
        view_pos = self.canvas.yview()
        content_height = self.scaled_image_height
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
                    self.draw_image_markers()  # 立即刷新标记
                else:
                    messagebox.showwarning("错误", "时间格式不正确，请使用格式如: 1分23秒")
            except Exception as e:
                messagebox.showwarning("错误", f"时间解析出错: {str(e)}")

    def parse_time_input(self, time_str):
        """解析时间输入为总秒数"""
        pattern = r'(\d+)分(\d+)秒'
        match = re.match(pattern, time_str.strip())
        if match:
            minutes = int(match.group(1))
            seconds = int(match.group(2))
            return minutes * 60 + seconds
        # 兼容纯数字格式（秒）
        if time_str.isdigit():
            return int(time_str)
        return None

    def save_timestamp_to_config(self, timestamp_time, position, is_home=False):
        """保存新时间戳到配置文件"""
        try:
            os.makedirs('source', exist_ok=True)
            config_path = 'source/tabs-config.json'

            # 读取配置
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {}

            # 初始化配置结构
            if self.tab_name not in config:
                config[self.tab_name] = {}
            if 'scroll' not in config[self.tab_name]:
                config[self.tab_name]['scroll'] = []

            # 去重后添加新时间戳
            new_point = {
                'time': round(timestamp_time, 2),
                'position': int(position),
                'home': is_home
            }
            config[self.tab_name]['scroll'] = [p for p in config[self.tab_name]['scroll'] if
                                               not (abs(p['time'] - new_point['time']) < 0.1)]
            config[self.tab_name]['scroll'].append(new_point)
            config[self.tab_name]['scroll'].sort(key=lambda x: x['time'])

            # 保存配置
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            messagebox.showinfo("成功", "时间戳保存成功！")

        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{str(e)}")

    def get_current_scroll_data(self):
        """获取当前标签的时间戳数据"""
        scroll_data = []
        config_path = 'source/tabs-config.json'

        try:
            if not os.path.exists(config_path):
                return scroll_data

            if not self.tab_name:
                return scroll_data

            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            if self.tab_name in config and isinstance(config[self.tab_name].get('scroll'), list):
                scroll_data = config[self.tab_name]['scroll']

        except Exception as e:
            return
        return scroll_data

    def draw_image_markers(self):
        """直接在图片Canvas上绘制时间戳标记（支持点击/拖动）"""
        # 清除原有标记（保留图片和点击测试标记）
        self.canvas.delete("timestamp_marker")
        self.canvas.delete("test_marker")
        # 重置标记-数据映射
        self.marker_id_to_data.clear()
        # 2. 绘制时间戳标记（支持点击/拖动）
        if not self.combined_image_path or not os.path.exists(self.combined_image_path):
            return

        scroll_data = self.get_current_scroll_data()
        if not scroll_data:
            return

        # 计算缩放比例（原始position → 缩放后图片坐标）
        scale_ratio = self.scaled_image_height / self.original_image_height if self.original_image_height > 0 else 1.0
        marker_x = 20  # 标记固定在左侧20px位置

        drawn_count = 0
        for item in scroll_data:
            # 原始position转换为缩放后的图片坐标
            scaled_y = item['position'] * scale_ratio

            # 绘制标记（区分home和普通标记）
            if item['home']:
                # home=true：红色实心圆
                marker_id = self.canvas.create_oval(
                    marker_x - 4, scaled_y - 4, marker_x + 4, scaled_y + 4,
                    fill='red', outline='red', tags='timestamp_marker'
                )
            else:
                # home=false：白色空心圆
                marker_id = self.canvas.create_oval(
                    marker_x - 4, scaled_y - 4, marker_x + 4, scaled_y + 4,
                    fill='yellow', outline='yellow', width=2, tags='timestamp_marker'
                )

            # ========== 关键：建立标记ID与数据项的映射 ==========
            self.marker_id_to_data[marker_id] = item

            # 绑定标记的按下事件（开始拖动）
            self.canvas.tag_bind(marker_id, '<Button-1>', lambda e, mid=marker_id: self.start_marker_drag(e, mid))
            self.canvas.tag_bind(marker_id, '<Button-3>', lambda e, mid=marker_id: self.edit_marker_time(mid))
            drawn_count += 1

        # 将标记置于图片上方（确保不被遮挡）
        self.canvas.tag_raise("timestamp_marker")
        self.canvas.tag_raise("test_marker")
        self.canvas.tag_raise("click_marker")

    def start_marker_drag(self, event, marker_id):
        """开始拖动标记：记录拖动状态"""
        self.dragging_marker_id = marker_id
        self.drag_start_y = self.canvas.canvasy(event.y)
        # 更改标记样式（提示正在拖动）
        self.canvas.itemconfig(marker_id, outline='yellow', width=3)
    def get_current_and_next_timestamp(self, scroll_data, current_time):
        # 定义容差（保持原逻辑的0.1秒）
        TOLERANCE = 0.1

        # 生成带缩放后position的时间戳列表（保留所有数据，后续统一排序过滤）
        timestamp_items = [
            (
                item['time'],
                item['position'],
                item['home'],
                # 计算缩放后的position（兼容原逻辑）
                item['position'] * (self.scaled_image_height / self.original_image_height)
                if self.original_image_height > 0 else 1.0
            )
            for item in scroll_data
        ]

        # 按时间戳升序排序（核心：保证时间顺序）
        timestamp_items.sort(key=lambda x: x[0])

        current_ts = None  # 存储当前匹配的时间戳
        next_ts = None     # 存储紧邻的下一个时间戳

        # 1. 找当前时间戳：不大于 current_time + TOLERANCE 的最大时间戳
        for ts in timestamp_items:
            ts_time = ts[0]
            if ts_time <= current_time + TOLERANCE:
                current_ts = ts  # 遍历到最后一个符合条件的即为最大的
            else:
                current_ts = [0,0,0,0]
                break  # 排序后，后续时间更大，无需继续

        # 2. 找下一个时间戳：大于 current_time - TOLERANCE 的最小时间戳
        for ts in timestamp_items:
            ts_time = ts[0]
            if ts_time > current_time - TOLERANCE:
                next_ts = ts
                break  # 排序后第一个符合条件的即为最小的

        # 边界处理：如果当前时间戳存在，但下一个时间戳在当前之前，取当前的下一个元素
        if current_ts and next_ts:
            if next_ts[0] <= current_ts[0] and timestamp_items.index(current_ts) < len(timestamp_items) - 1:
                next_ts = timestamp_items[timestamp_items.index(current_ts) + 1]

        # 最终兜底：如果下一个时间戳为空，但有当前时间戳且不是最后一个元素
        if not next_ts and current_ts:
            current_idx = timestamp_items.index(current_ts)
            if current_idx < len(timestamp_items) - 1:
                next_ts = timestamp_items[current_idx + 1]

        return current_ts, next_ts

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
        self.target_view_fraction = self.canvas.yview()[0]
        self.auto_scroll_btn.configure(text="⏹ 停止滚动", bg='red')
        self.auto_scroll_step()

    def stop_auto_scroll(self):
        """停止自动滚动"""
        self.is_auto_scrolling = False
        if self.auto_scroll_after_id:
            self.root.after_cancel(self.auto_scroll_after_id)
        self.auto_scroll_btn.configure(text="▶ 自动滚动", bg='white')

    def auto_scroll_step(self):
        """自动滚动核心逻辑（基于M位置判断）"""
        if not self.is_auto_scrolling:
            return

        elapsed_time = time.time() - self.start_time
        scroll_data = self.get_current_scroll_data()
        if not scroll_data:
            # 无数据时缓慢滚动
            current_fraction = self.canvas.yview()[0]
            self.target_view_fraction = min(1.0, current_fraction + self.smooth_step)
            self.smooth_scroll_to(self.target_view_fraction)

            # 到底后停止
            if self.canvas.yview()[1] >= 0.99:
                self.stop_auto_scroll()
                return
        else:
            # 有时间戳时：基于M位置判断滚动逻辑
            current_ts,next_ts = self.get_current_and_next_timestamp(scroll_data, elapsed_time)
            if next_ts:

                next_time, next_pos, next_home, next_scaled_y = next_ts
                current_time, current_pos, current_home, current_scaled_y = current_ts
                # 计算该标记在视口中的当前位置

                next_ratio = next_scaled_y / self.scaled_image_height
                current_ratio = current_scaled_y / self.scaled_image_height
                if next_home:
                    # 是起始点
                    if elapsed_time >= next_time - 0.02:
                        self.canvas.yview_moveto(next_ratio)
                    else:
                        pass
                else:
                    # 不是起始点
                    self.smooth_scroll_to(next_time,next_ratio,elapsed_time)
            else:
                # 无后续时间戳：停止滚动
                self.stop_auto_scroll()
                return

        # 持续回调实现平滑滚动
        self.auto_scroll_after_id = self.root.after(self.smooth_refresh_ms, self.auto_scroll_step)

    def smooth_scroll_to(self,next_time,target_fraction,elapsed_time):
        """真正的平滑滚动：每次移动一小步，直到到达目标"""
        current_top_fraction = self.canvas.yview()[0]
        current_botton_fraction = self.canvas.yview()[1]
        m_fraction = (current_botton_fraction - current_top_fraction)*self.screen_marker_pos+current_top_fraction
        remaining_time = max(0.01, next_time - elapsed_time)
        # 按步长逐步接近目标
        step = float(self.smooth_refresh_ms/1000)*(target_fraction-m_fraction)/remaining_time
        new_fraction = m_fraction + step
        self.canvas.yview_moveto(new_fraction-(current_botton_fraction - current_top_fraction)*self.screen_marker_pos)

    def exit_fullscreen(self):
        """退出全屏并清理资源"""
        self.stop_auto_scroll()
        self.root.destroy()


# 测试代码（直接运行时生效）
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    app = FullScreenImageWindow()
    root.mainloop()