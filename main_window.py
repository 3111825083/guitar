# main_window.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from PIL import Image, ImageTk

from components.guitartab_manager import GuitarTabManager
from fullscreen_window import FullScreenImageWindow


class MainWindow:
    """主窗口"""

    def __init__(self, root):
        self.root = root
        self.root.title("吉他谱查看器")
        self.root.geometry("1200x800")

        self.tab_manager = GuitarTabManager()
        self.init_ui()
        self.refresh_tab_list()

    def init_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建左右分割
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        # 创建左侧列表面板
        self.create_list_panel(paned_window)

        # 创建右侧详情面板
        self.create_detail_panel(paned_window)

        # 添加面板到分割窗口
        paned_window.add(self.list_panel)
        paned_window.add(self.detail_panel)

    def create_list_panel(self, parent):
        """创建左侧列表面板"""
        self.list_panel = ttk.Frame(parent)
        self.list_panel.pack(fill=tk.BOTH, expand=True)

        # 搜索框框架
        search_frame = ttk.Frame(self.list_panel)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        self.search_input = ttk.Entry(search_frame)
        self.search_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_input.insert(0, "搜索歌曲名/歌手/类型...")
        self.search_input.bind("<FocusIn>", lambda e: self.search_input.delete(0,
                                                                               tk.END) if self.search_input.get() == "搜索歌曲名/歌手/类型..." else None)
        self.search_input.bind("<FocusOut>", lambda e: self.search_input.insert(0,
                                                                                "搜索歌曲名/歌手/类型...") if not self.search_input.get() else None)
        self.search_input.bind("<KeyRelease>", self.on_search_changed)

        # 添加歌曲按钮
        self.add_song_btn = ttk.Button(search_frame, text="+ 添加歌曲", command=self.add_new_song)
        self.add_song_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # 列表
        list_frame = ttk.Frame(self.list_panel)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # 创建Treeview
        columns = ('歌曲名', '歌手')
        self.tab_list_widget = ttk.Treeview(list_frame, columns=columns, show='headings', height=20)
        self.tab_list_widget.heading('歌曲名', text='歌曲名')
        self.tab_list_widget.heading('歌手', text='歌手')
        self.tab_list_widget.column('歌曲名', width=150)
        self.tab_list_widget.column('歌手', width=150)

        # 滚动条
        list_scrollbar_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tab_list_widget.yview)
        list_scrollbar_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.tab_list_widget.xview)
        self.tab_list_widget.configure(yscrollcommand=list_scrollbar_y.set, xscrollcommand=list_scrollbar_x.set)

        # 布局
        self.tab_list_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        list_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        # 绑定选择事件
        self.tab_list_widget.bind('<<TreeviewSelect>>', self.on_tab_selected)

    def add_new_song(self):
        """添加新歌曲"""
        # 创建添加歌曲对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("添加新歌曲")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        # 创建对话框内容
        dialog_frame = ttk.Frame(dialog)
        dialog_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 表单
        form_frame = ttk.LabelFrame(dialog_frame, text="歌曲信息")
        form_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(form_frame, text="歌曲名:").grid(row=0, column=0, sticky=tk.W, pady=5)
        song_name_input = ttk.Entry(form_frame)
        song_name_input.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=(10, 0))

        ttk.Label(form_frame, text="歌手:").grid(row=1, column=0, sticky=tk.W, pady=5)
        singer_input = ttk.Entry(form_frame)
        singer_input.grid(row=1, column=1, sticky=tk.EW, pady=5, padx=(10, 0))

        ttk.Label(form_frame, text="类型:").grid(row=2, column=0, sticky=tk.W, pady=5)
        type_var = tk.StringVar()
        type_combo = ttk.Combobox(form_frame, textvariable=type_var, values=["弹唱", "指弹", "独奏", "合奏"],
                                  state="readonly")
        type_combo.grid(row=2, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        type_combo.current(0)

        form_frame.columnconfigure(1, weight=1)

        # 按钮框架
        button_frame = ttk.Frame(dialog_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))

        def confirm_add():
            song_name = song_name_input.get().strip()
            singer = singer_input.get().strip()
            song_type = type_var.get()

            if song_name and singer:
                # 检查歌曲是否已存在
                existing_tabs = self.tab_manager.get_all_tabs()
                if song_name in existing_tabs:
                    messagebox.showwarning("警告", f"歌曲 '{song_name}' 已存在！")
                    return

                # 创建新的歌曲信息
                new_song_info = {
                    "artist": singer,
                    "type": song_type,
                    "views": "0",
                    "downloads": "0",
                    "pages": 0
                }

                # 添加到配置中
                if self.tab_manager.add_tab(song_name, new_song_info):
                    # 创建对应的文件夹
                    source_dir = f"source/{song_name}"
                    if not os.path.exists(source_dir):
                        os.makedirs(source_dir)

                    # 刷新列表
                    self.refresh_tab_list()
                    messagebox.showinfo("成功", f"歌曲 '{song_name}' 添加成功！")
                    dialog.destroy()
                else:
                    messagebox.showerror("错误", "添加歌曲失败！")
            else:
                messagebox.showwarning("警告", "歌曲名和歌手不能为空！")

        ok_button = ttk.Button(button_frame, text="确定", command=confirm_add)
        cancel_button = ttk.Button(button_frame, text="取消", command=dialog.destroy)

        ok_button.pack(side=tk.RIGHT, padx=(5, 0))
        cancel_button.pack(side=tk.RIGHT)

        # 居中显示对话框
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

    def upload_guitar_tabs(self):
        """上传吉他谱图片"""
        if not self.current_tab_name:
            messagebox.showwarning("警告", "请先选择一首歌曲！")
            return

        # 选择图片文件
        file_paths = filedialog.askopenfilenames(
            title="选择吉他谱图片",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg")]
        )

        if file_paths:
            source_dir = f"source/{self.current_tab_name}"

            # 复制文件到对应目录
            success_count = 0
            for i, file_path in enumerate(file_paths):
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
                messagebox.showinfo("成功", f"成功上传 {success_count} 张吉他谱图片！")
                # 重新加载当前歌曲的图片
                if self.current_tab_name:
                    self.load_tab_image()
            else:
                messagebox.showwarning("警告", "没有成功上传任何图片！")

    def create_detail_panel(self, parent):
        """创建右侧详情面板"""
        self.detail_panel = ttk.Frame(parent)
        self.detail_panel.pack(fill=tk.BOTH, expand=True)

        # 标题区域
        title_frame = ttk.Frame(self.detail_panel)
        title_frame.pack(fill=tk.X, pady=(0, 10))

        self.title_label = ttk.Label(title_frame, text="请选择吉他谱", font=("Arial", 16, "bold"))
        self.title_label.pack(side=tk.LEFT)

        # 收藏按钮
        self.favorite_btn = ttk.Button(title_frame, text="★ 收藏", command=self.toggle_favorite)
        self.favorite_btn.pack(side=tk.RIGHT)

        # 信息展示区域
        info_frame = ttk.LabelFrame(self.detail_panel, text="基本信息")
        info_frame.pack(fill=tk.X, pady=(0, 10))

        info_grid = ttk.Frame(info_frame)
        info_grid.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(info_grid, text="歌手:").grid(row=0, column=0, sticky=tk.W)
        self.singer_label = ttk.Label(info_grid, text="")
        self.singer_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        ttk.Label(info_grid, text="类型:").grid(row=1, column=0, sticky=tk.W)
        self.type_label = ttk.Label(info_grid, text="")
        self.type_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))

        ttk.Label(info_grid, text="浏览量:").grid(row=2, column=0, sticky=tk.W)
        self.view_label = ttk.Label(info_grid, text="")
        self.view_label.grid(row=2, column=1, sticky=tk.W, padx=(10, 0))

        ttk.Label(info_grid, text="下载量:").grid(row=3, column=0, sticky=tk.W)
        self.download_label = ttk.Label(info_grid, text="")
        self.download_label.grid(row=3, column=1, sticky=tk.W, padx=(10, 0))

        # 图片展示区域
        image_frame = ttk.Frame(self.detail_panel)
        image_frame.pack(fill=tk.BOTH, expand=True)

        self.image_canvas = tk.Canvas(image_frame, bg="white")
        self.image_canvas.pack(fill=tk.BOTH, expand=True)

        # 滚动条
        image_scrollbar_y = ttk.Scrollbar(image_frame, orient=tk.VERTICAL, command=self.image_canvas.yview)
        image_scrollbar_x = ttk.Scrollbar(image_frame, orient=tk.HORIZONTAL, command=self.image_canvas.xview)
        self.image_canvas.configure(yscrollcommand=image_scrollbar_y.set, xscrollcommand=image_scrollbar_x.set)

        # 布局
        self.image_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        image_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        image_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        # 添加鼠标双击事件
        self.image_canvas.bind("<Double-Button-1>", self.toggle_fullscreen)

        # 控制按钮
        control_frame = ttk.Frame(self.detail_panel)
        control_frame.pack(fill=tk.X, pady=(10, 0))

        self.prev_btn = ttk.Button(control_frame, text="上一页", command=self.prev_page)
        self.prev_btn.pack(side=tk.LEFT)

        self.page_label = ttk.Label(control_frame, text="第 1 页")
        self.page_label.pack(side=tk.LEFT, padx=10)

        self.next_btn = ttk.Button(control_frame, text="下一页", command=self.next_page)
        self.next_btn.pack(side=tk.LEFT)

        control_frame.columnconfigure(1, weight=1)

        ttk.Button(control_frame, text="上传谱子", command=self.upload_guitar_tabs).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(control_frame, text="下载", command=self.download_tab).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(control_frame, text="打印", command=self.print_tab).pack(side=tk.RIGHT, padx=(5, 0))

        self.current_tab_name = None
        self.current_tab = None
        self.current_page = 1
        self.total_pages = 0
        self.photo_image = None

    def refresh_tab_list(self):
        """刷新吉他谱列表"""
        # 清空现有项目
        for item in self.tab_list_widget.get_children():
            self.tab_list_widget.delete(item)

        tabs = self.tab_manager.get_all_tabs()
        for name, info in tabs.items():
            singer = info.get('artist', '')
            self.tab_list_widget.insert('', tk.END, values=(name, singer), iid=name)

    def on_search_changed(self, event):
        """搜索框内容改变时"""
        pass  # 实时搜索可在此实现

    def on_tab_selected(self, event):
        """选择吉他谱"""
        selection = self.tab_list_widget.selection()
        if selection:
            tab_name = selection[0]
            self.current_tab_name = tab_name
            self.current_tab = self.tab_manager.get_tab_detail(tab_name)
            self.current_page = 1
            self.load_tab_detail(tab_name)

    def load_tab_detail(self, tab_name):
        """加载吉他谱详情"""
        if not self.current_tab:
            return

        # 更新基本信息
        self.title_label.config(text=f"{tab_name} - {self.current_tab.get('artist', '')}")
        self.singer_label.config(text=self.current_tab.get('artist', ''))
        self.type_label.config(text=self.current_tab.get('type', ''))
        self.view_label.config(text=self.current_tab.get('views', '0'))
        self.download_label.config(text=self.current_tab.get('downloads', '0'))

        # 加载第一页图片
        self.load_tab_image()

    def load_tab_image(self):
        """加载当前页图片"""
        if not self.current_tab_name:
            return

        image_path = f"source/{self.current_tab_name}/{self.current_page}.png"
        if os.path.exists(image_path):
            try:
                # 打开图片并调整大小
                img = Image.open(image_path)

                # 获取画布大小
                canvas_width = self.image_canvas.winfo_width()
                canvas_height = self.image_canvas.winfo_height()

                # 如果是初始状态，使用默认大小
                if canvas_width <= 1:
                    canvas_width = 400
                if canvas_height <= 1:
                    canvas_height = 600

                # 调整图片大小以适应画布
                img.thumbnail((canvas_width - 20, canvas_height - 20), Image.Resampling.LANCZOS)

                # 转换为PhotoImage
                self.photo_image = ImageTk.PhotoImage(img)

                # 清空画布并显示新图片
                self.image_canvas.delete("all")
                self.image_canvas.create_image(canvas_width // 2, canvas_height // 2, image=self.photo_image)
                self.image_canvas.config(scrollregion=self.image_canvas.bbox("all"))

                self.page_label.config(text=f"第 {self.current_page} 页")
            except Exception as e:
                self.image_canvas.delete("all")
                self.image_canvas.create_text(200, 300, text="图片加载失败", fill="black")
        else:
            self.image_canvas.delete("all")
            self.image_canvas.create_text(200, 300, text="未找到图片文件", fill="black")

    def prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_tab_image()

    def next_page(self):
        """下一页"""
        if self.current_tab_name:
            self.current_page += 1
            # 检查下一页是否存在
            next_image_path = f"source/{self.current_tab_name}/{self.current_page}.png"
            if os.path.exists(next_image_path):
                self.load_tab_image()
            else:
                self.current_page -= 1  # 回退

    def toggle_favorite(self):
        """切换收藏状态"""
        if self.current_tab_name:
            if self.tab_manager.is_favorite(self.current_tab_name):
                self.tab_manager.remove_favorite(self.current_tab_name)
                messagebox.showinfo("提示", f"已取消收藏: {self.current_tab_name}")
            else:
                self.tab_manager.add_favorite(self.current_tab_name)
                messagebox.showinfo("提示", f"已添加收藏: {self.current_tab_name}")

    def download_tab(self):
        """下载吉他谱"""
        if self.current_tab:
            messagebox.showinfo("下载", "开始下载选中的吉他谱...")

    def print_tab(self):
        """打印吉他谱"""
        if self.current_tab:
            messagebox.showinfo("打印", "开始打印选中的吉他谱...")

    def toggle_fullscreen(self, event):
        """切换全屏模式"""
        fullscreen_window = FullScreenImageWindow(self)
        fullscreen_window.load_image(self.current_tab_name)

    def key_press_event(self, event):
        """处理按键事件"""
        if event.keysym == "Escape":
            # 退出全屏逻辑可以在这里实现
            pass