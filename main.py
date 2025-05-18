import tkinter as tk
from tkinter import ttk, messagebox
from uszipcode import SearchEngine
import pytz
from datetime import datetime
import re
import os

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# 颜色方案
BG_COLOR = "#f7f9fa"  # 浅色背景
FG_COLOR = "#222"      # 深色文字
ACCENT_COLOR = "#1976d2"  # 蓝色强调色
ERROR_COLOR = "#d32f2f"   # 红色
SUCCESS_COLOR = "#388e3c" # 绿色
CARD_COLOR = "#fff"
GRAY_LABEL = "#bdbdbd"
SHADOW_COLOR = "#e0e3e7"

FONT_FAMILY = ("微软雅黑", "苹方", "Arial", "Roboto", "sans-serif")

class RoundedFrame(tk.Canvas):
    # 用于模拟圆角卡片
    def __init__(self, parent, width, height, radius=18, bg=CARD_COLOR, shadow=True, **kwargs):
        tk.Canvas.__init__(self, parent, width=width, height=height, bg=BG_COLOR, highlightthickness=0, bd=0)
        self.radius = radius
        self.bg = bg
        self.shadow = shadow
        self.width = width
        self.height = height
        self.create_card()
        self.inner = tk.Frame(self, bg=bg, bd=0)
        self.create_window((radius, radius), window=self.inner, anchor="nw")
    def create_card(self):
        r = self.radius
        w, h = self.width, self.height
        if self.shadow:
            self.create_rounded_rect(r+2, r+2, w-2, h-2, r, fill=SHADOW_COLOR, outline="", tags="shadow")
        self.create_rounded_rect(0, 0, w-4, h-4, r, fill=self.bg, outline="", tags="card")
    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [x1+r, y1,
                  x2-r, y1,
                  x2, y1,
                  x2, y1+r,
                  x2, y2-r,
                  x2, y2,
                  x2-r, y2,
                  x1+r, y2,
                  x1, y2,
                  x1, y2-r,
                  x1, y1+r,
                  x1, y1]
        return self.create_polygon(points, smooth=True, **kwargs)

class ChipLabel(tk.Label):
    # Material风格Chip标签
    def __init__(self, parent, text, bg, fg, icon=None, active=False, **kwargs):
        font = (FONT_FAMILY, 16, "bold")
        super().__init__(parent, text=(icon+" "+text) if icon else text, bg=bg, fg=fg, font=font, padx=16, pady=2, bd=0)
        self.configure(relief="flat", cursor="hand2" if active else "arrow")
        self.active = active
        self.default_bg = bg
        self.default_fg = fg
        self.icon = icon
        self.text = text
        self.update_style(active)
    def update_style(self, active):
        if active:
            self.configure(bg=self.default_bg, fg=self.default_fg)
        else:
            self.configure(bg="#e0e0e0", fg="#888")

class ZipTimezoneApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TK电话邀约时区查询")
        self.geometry("760x600")
        self.resizable(False, False)
        self.configure(bg=BG_COLOR)
        self.search_engine = SearchEngine()
        self._set_style()
        self._build_ui()
        self.zip_entry.focus_set()
        self._timer_id = None  # 用于定时器管理

    def _set_style(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TButton', font=(FONT_FAMILY, 18, 'bold'), padding=8, borderwidth=0, relief="flat")
        style.configure('Accent.TButton', background=ACCENT_COLOR, foreground='white', borderwidth=0, relief="flat")
        style.map('Accent.TButton', background=[('active', '#1565c0')])
        style.configure('TLabel', background=BG_COLOR, foreground=FG_COLOR, font=(FONT_FAMILY, 16))
        style.configure('Result.TLabel', font=(FONT_FAMILY, 20, 'bold'), foreground=ACCENT_COLOR, background=BG_COLOR)
        style.configure('Error.TLabel', font=(FONT_FAMILY, 14), foreground=ERROR_COLOR, background=BG_COLOR)
        style.configure('Time.TLabel', font=(FONT_FAMILY, 32, 'bold'), foreground=FG_COLOR, background=BG_COLOR)
        style.configure('Gray.TLabel', font=(FONT_FAMILY, 12), foreground=GRAY_LABEL, background=BG_COLOR)

    def _build_ui(self):
        # 顶部Logo+应用名
        top_frame = tk.Frame(self, bg=BG_COLOR)
        top_frame.pack(fill=tk.X, pady=(32, 12))

        centered_frame = tk.Frame(top_frame, bg=BG_COLOR)
        centered_frame.pack(anchor="center")  # 让logo+标题整体居中

        # logo
        logo_path = os.path.join("img", "fengqianlogo2.png")
        print("logo_path:", logo_path, "exists:", os.path.exists(logo_path))  # 调试用
        logo_loaded = False
        if PIL_AVAILABLE and os.path.exists(logo_path):
            logo_img = Image.open(logo_path).resize((48, 48))
            self.logo_img = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(centered_frame, image=self.logo_img, bg=BG_COLOR, bd=0)
            logo_label.pack(side=tk.LEFT, padx=(0, 16))  # 只在logo和标题之间加间距
            logo_loaded = True
        if not logo_loaded:
            logo_fail_label = tk.Label(centered_frame, text="Logo加载失败", font=(FONT_FAMILY, 10), fg=ERROR_COLOR, bg=BG_COLOR)
            logo_fail_label.pack(side=tk.LEFT, padx=(0, 16))

        # 标题
        title_label = tk.Label(centered_frame, text="TK电话邀约时区查询", font=(FONT_FAMILY, 32, "bold"), fg=ACCENT_COLOR, bg=BG_COLOR)
        title_label.pack(side=tk.LEFT)

        # 主体内容center_frame，所有内容居中
        center_frame = tk.Frame(self, bg=BG_COLOR, width=700)
        center_frame.pack(expand=True, anchor="center")

        # 输入区
        input_frame = tk.Frame(center_frame, bg=BG_COLOR)
        input_frame.pack(pady=(0, 24), anchor="center")
        entry_bg = tk.Frame(input_frame, bg="#fff", highlightbackground=ACCENT_COLOR, highlightcolor=ACCENT_COLOR, highlightthickness=2, bd=0)
        entry_bg.pack(side=tk.LEFT, padx=(0, 16))
        self.zip_entry = tk.Entry(
            entry_bg,
            width=14,
            font=(FONT_FAMILY, 20),
            bd=0,
            relief="flat",
            fg=FG_COLOR,  # 深灰
            bg="#fff",
            insertbackground=ACCENT_COLOR,  # 光标蓝色
            highlightcolor=ACCENT_COLOR,    # 聚焦边框蓝色
            highlightthickness=0            # Entry本身不需要边框
        )
        self.zip_entry.pack(ipady=8, ipadx=2)
        self.zip_entry.insert(0, "请输入美国ZIP码")
        self.zip_entry.bind("<FocusIn>", self._clear_placeholder)
        self.zip_entry.bind("<Return>", self._on_query)
        query_btn = ttk.Button(input_frame, text="查询", style='Accent.TButton', command=self._on_query)
        query_btn.pack(side=tk.LEFT, ipadx=18, ipady=8)
        self.query_btn = query_btn
        # 错误提示
        self.error_label = tk.Label(center_frame, text="", font=(FONT_FAMILY, 13), fg=ERROR_COLOR, bg=BG_COLOR)
        self.error_label.pack(pady=(8, 0), anchor="center")

        # 睡觉/正常时间chip标签区（居中且宽度与卡片一致）
        chip_frame2 = tk.Frame(center_frame, bg=BG_COLOR, width=600, height=40)
        chip_frame2.pack(pady=(24, 24))
        chip_frame2.pack_propagate(False)
        self.sleep_chip = ChipLabel(chip_frame2, "睡觉时间", ERROR_COLOR, "#fff", icon="🌙", active=False)
        self.normal_chip = ChipLabel(chip_frame2, "正常时间", SUCCESS_COLOR, "#fff", icon="☀️", active=False)
        self.sleep_chip.grid(row=0, column=0, padx=(0, 18), pady=0, sticky="ew")
        self.normal_chip.grid(row=0, column=1, padx=(0, 0), pady=0, sticky="ew")
        chip_frame2.grid_columnconfigure(0, weight=1)
        chip_frame2.grid_columnconfigure(1, weight=1)

        # 结果卡片区域
        card = RoundedFrame(center_frame, width=600, height=300, radius=18, bg=CARD_COLOR, shadow=True)
        card.pack(pady=(0, 28), anchor="center")
        self.card_inner = card.inner
        # 分组标签行
        label_row = tk.Frame(self.card_inner, bg=CARD_COLOR)
        label_row.pack(pady=(18, 0), anchor="center")
        self.city_label = tk.Label(label_row, text="城市", font=(FONT_FAMILY, 13), fg=GRAY_LABEL, bg=CARD_COLOR, anchor="center", justify="center")
        self.city_label.pack(side=tk.LEFT, padx=40)
        self.state_label = tk.Label(label_row, text="州", font=(FONT_FAMILY, 13), fg=GRAY_LABEL, bg=CARD_COLOR, anchor="center", justify="center")
        self.state_label.pack(side=tk.LEFT, padx=40)
        self.tzname_label = tk.Label(label_row, text="美国时区", font=(FONT_FAMILY, 13), fg=GRAY_LABEL, bg=CARD_COLOR, anchor="center", justify="center")
        self.tzname_label.pack(side=tk.LEFT, padx=40)
        # 内容行
        value_row = tk.Frame(self.card_inner, bg=CARD_COLOR)
        value_row.pack(pady=(0, 0), anchor="center")
        self.city_val = tk.Label(value_row, text="-", font=(FONT_FAMILY, 20, "bold"), fg=FG_COLOR, bg=CARD_COLOR, anchor="center", justify="center")
        self.city_val.pack(side=tk.LEFT, padx=40)
        self.state_val = tk.Label(value_row, text="-", font=(FONT_FAMILY, 20, "bold"), fg=FG_COLOR, bg=CARD_COLOR, anchor="center", justify="center")
        self.state_val.pack(side=tk.LEFT, padx=40)
        self.tzname_val = tk.Label(value_row, text="-", font=(FONT_FAMILY, 20, "bold"), fg=ACCENT_COLOR, bg=CARD_COLOR, anchor="center", justify="center")
        self.tzname_val.pack(side=tk.LEFT, padx=40)
        # 时间
        self.time_label = tk.Label(self.card_inner, text="当前时间", font=(FONT_FAMILY, 36, "bold"), fg=FG_COLOR, bg=CARD_COLOR, anchor="center", justify="center")
        self.time_label.pack(pady=(18, 0), anchor="center")
        self.date_label = tk.Label(self.card_inner, text="", font=(FONT_FAMILY, 16), fg=GRAY_LABEL, bg=CARD_COLOR, anchor="center", justify="center")
        self.date_label.pack(pady=(0, 10), anchor="center")
        # chip标签区
        self.chip_frame = tk.Frame(self.card_inner, bg=CARD_COLOR)
        self.chip_frame.pack(pady=(10, 0), anchor="center")
        self.dst_chip = ChipLabel(self.chip_frame, "夏令时", ACCENT_COLOR, "#fff", icon="⏱", active=False)
        self.dst_chip.pack(side=tk.LEFT, padx=(0, 18))
        self.utc_chip = ChipLabel(self.chip_frame, "UTC偏移", GRAY_LABEL, "#fff", icon="🌐", active=False)
        self.utc_chip.pack(side=tk.LEFT, padx=(0, 0))

    def _clear_placeholder(self, event):
        if self.zip_entry.get() == "请输入美国ZIP码":
            self.zip_entry.delete(0, tk.END)
            self.zip_entry.config(fg=FG_COLOR, insertbackground=ACCENT_COLOR)

    def _on_query(self, event=None):
        zip_input = self.zip_entry.get().strip()
        zip_code = self.validate_zip(zip_input)
        self.error_label.config(text="")
        if not zip_code:
            self._show_error('⚠️ 请输入有效的5位ZIP码')
            self._clear_result()
            return
        try:
            zipcode_info = self.search_engine.by_zipcode(zip_code)
            if not zipcode_info or not zipcode_info.timezone:
                self._show_error('⚠️ 未找到该ZIP码对应的时区信息')
                self._clear_result()
                return
            self._show_error("")
            self.show_timezone_info(zip_code, zipcode_info)
        except Exception as e:
            self._show_error(f'⚠️ 查询失败: {str(e)}')
            self._clear_result()

    def _show_error(self, msg):
        self.error_label.config(text=msg)

    def _clear_result(self):
        self.city_val.config(text="-")
        self.state_val.config(text="-")
        self.tzname_val.config(text="-")
        self.time_label.config(text="当前时间")
        self.date_label.config(text="")
        self.dst_chip.config(text="夏令时", bg=ACCENT_COLOR, fg="#fff")
        self.utc_chip.config(text="UTC偏移", bg=GRAY_LABEL, fg="#fff")
        self.sleep_chip.update_style(False)
        self.normal_chip.update_style(False)
        # 取消定时器
        if hasattr(self, '_timer_id') and self._timer_id:
            self.after_cancel(self._timer_id)
            self._timer_id = None

    def validate_zip(self, zip_input):
        match = re.match(r'^(\d{5})', zip_input)
        if match:
            return match.group(1)
        return None

    def show_timezone_info(self, zip_code, zipcode_info):
        timezone_name = zipcode_info.timezone
        city = zipcode_info.major_city or '-'
        state = zipcode_info.state or '-'
        tz_us_name_map = {
            'America/New_York': 'Eastern Time',
            'America/Chicago': 'Central Time',
            'America/Denver': 'Mountain Time',
            'America/Phoenix': 'Mountain Time (Arizona)',
            'America/Los_Angeles': 'Pacific Time',
            'America/Anchorage': 'Alaska Time',
            'Pacific/Honolulu': 'Hawaii-Aleutian Time',
        }
        us_tz_name = tz_us_name_map.get(timezone_name, '未知/其他')
        try:
            tz = pytz.timezone(timezone_name)
        except Exception:
            self._show_error('⚠️ 时区数据异常')
            self._clear_result()
            return
        now = datetime.now(tz)
        is_dst = bool(now.dst())
        utc_offset = now.utcoffset().total_seconds() / 3600
        dst_str = '是' if is_dst else '否'
        # 更新卡片内容
        self.city_val.config(text=city)
        self.state_val.config(text=state)
        self.tzname_val.config(text=us_tz_name)
        self.time_label.config(text=now.strftime('%I:%M:%S %p'))
        self.date_label.config(text=now.strftime('%m/%d/%Y'))
        # chip标签
        self.dst_chip.config(text=f"夏令时: {dst_str}", bg=ACCENT_COLOR if is_dst else GRAY_LABEL, fg="#fff")
        self.utc_chip.config(text=f"UTC{utc_offset:+.0f}", bg=ACCENT_COLOR, fg="#fff")
        # 睡觉/正常时间chip
        self.update_sleep_status(now)
        # 只保留一个定时器
        if self._timer_id:
            self.after_cancel(self._timer_id)
        self._timer_id = self.after(1000, lambda: self.show_timezone_info(zip_code, zipcode_info))

    def update_sleep_status(self, now):
        hour = now.hour
        if hour >= 21 or hour < 9:
            self.sleep_chip.update_style(True)
            self.normal_chip.update_style(False)
        else:
            self.sleep_chip.update_style(False)
            self.normal_chip.update_style(True)

if __name__ == "__main__":
    app = ZipTimezoneApp()
    app.mainloop() 