# ZIP码时区查询工具 - 产品需求文档 (PRD)

## 1. 产品概述

### 1.1 产品名称
ZIP码时区查询工具 (ZIP Timezone Lookup Tool)

### 1.2 产品定位
为非技术背景的实习生提供的简单易用的桌面应用程序，通过输入美国ZIP码快速查询对应的时区和当地时间。

### 1.3 目标用户
- 主要用户：没有开发基础的实习生
- 技术水平：计算机基础操作水平
- 使用场景：需要快速查询美国不同地区的时间信息

## 2. 功能需求

### 2.1 核心功能
1. **ZIP码输入**
   - 提供文本输入框，支持5位数字ZIP码输入
   - 支持ZIP+4格式（如12345-6789），但只使用前5位进行查询
   - 输入验证：确保输入为有效的美国ZIP码格式

2. **时区显示**
   - 显示对应ZIP码所属的标准时区名称（如"Eastern Time", "Pacific Time"等）
   - 显示UTC偏移量（如UTC-5, UTC-8等）
   - 显示是否处于夏令时状态

3. **当地时间显示**
   - 实时显示该时区的当前时间
   - 时间格式：12小时制，包含AM/PM
   - 日期格式：MM/DD/YYYY
   - 每秒自动更新时间显示

### 2.2 辅助功能
1. **错误处理**
   - 无效ZIP码提示
   - 网络连接错误处理
   - 数据查询失败提示

2. **用户体验优化**
   - 查询历史记录（最近5个查询）
   - 一键清除输入内容
   - 一键复制时间信息到剪贴板

## 3. 技术规格

### 3.1 平台要求
- **目标平台**：Windows 10/11
- **运行方式**：双击exe文件直接运行，无需安装
- **依赖要求**：无需额外安装任何运行环境

### 3.2 性能要求（优化后）
- 应用启动时间：≤ 2秒（仅需加载uszipcode数据）
- ZIP码查询响应时间：≤ 0.5秒（直接查询，无转换步骤）
- 内存占用：≤ 60MB（显著减少）
- 文件大小：≤ 30MB（去除pytzwhere相关文件）

### 3.3 数据源说明（简化版）
- **ZIP码时区数据**：uszipcode内置时区映射（基于美国邮政系统官方数据）
- **时间计算**：pytz库（基于IANA时区数据库）
- **数据优势**：双库架构，启动更快，查询更简单，文件更小

## 4. 界面设计规范

### 4.1 整体布局
- **窗口大小**：固定尺寸 400x300像素，不可调整大小
- **设计风格**：简洁、现代、易于理解
- **颜色方案**：浅色背景，深色文字，蓝色强调色

### 4.2 具体元素
1. **标题栏**
   - 应用名称："ZIP码时区查询"
   - 标准窗口控制按钮（最小化、关闭）

2. **输入区域**
   - 文本标签："请输入美国ZIP码："
   - 输入框：宽度200px，提示文字"如：10001"
   - 查询按钮："查询"，蓝色背景

3. **结果显示区域**
   - 时区信息显示框
   - 当前时间显示框（大字体，易读）
   - 状态提示区域

4. **功能按钮区域**
   - "清除"按钮
   - "复制时间"按钮
   - 历史记录下拉菜单

### 4.3 交互设计
- 支持回车键触发查询
- 输入框自动获取焦点
- 错误信息以红色显示
- 成功查询后输入框保持内容，方便修改

## 5. 用户操作流程

### 5.1 基本使用流程
1. 双击应用程序图标启动
2. 在输入框中输入5位ZIP码
3. 点击"查询"按钮或按回车键
4. 查看显示的时区和当地时间信息
5. 可选：复制时间信息或查看历史记录

### 5.2 错误处理流程
1. 输入无效ZIP码 → 显示"请输入有效的5位ZIP码"
2. 查询无结果 → 显示"未找到该ZIP码对应的时区信息"
3. 网络错误 → 显示"网络连接失败，请检查网络设置"

## 6. 开发实现指导

### 6.1 推荐技术栈（简化方案）
- **开发语言**：Python + tkinter
- **核心依赖**：uszipcode (ZIP码直接时区查询) + pytz (时区时间处理)
- **打包工具**：PyInstaller
- **备用库**：timezonefinder (仅在uszipcode无时区数据时使用)

### 6.2 关键实现点

#### 技术架构设计（简化版）
1. **核心查询链路**：
   ```
   ZIP码 → uszipcode(直接获取时区) → pytz(获取当前时间)
   ```

2. **主要依赖库**：
   - **uszipcode**：直接提供ZIP码到时区的映射，无需转换步骤
   - **pytz**：提供准确的时区时间计算和夏令时处理

3. **方案优势**：
   - 极简架构：只需两个库即可完成全部功能
   - 性能优异：减少了一层查询转换，响应更快
   - 数据可靠：uszipcode内置官方时区映射数据
   - 离线运行：所有数据本地存储，无网络依赖

#### 核心实现代码
```python
from uszipcode import SearchEngine
import pytz
from datetime import datetime

class ZipTimezoneQuery:
    def __init__(self):
        self.search_engine = SearchEngine(simple_zipcode=True)
    
    def get_timezone_info(self, zip_code):
        # 1. 通过ZIP码直接获取时区信息
        zipcode_info = self.search_engine.by_zipcode(zip_code)
        if not zipcode_info:
            return None, "ZIP码未找到"
        
        # 2. 获取时区名称（uszipcode直接提供）
        timezone_name = zipcode_info.timezone
        if not timezone_name:
            return None, "该ZIP码暂无时区信息"
        
        # 3. 计算当前时间
        tz = pytz.timezone(timezone_name)
        current_time = datetime.now(tz)
        
        return {
            'timezone_name': timezone_name,
            'current_time': current_time,
            'city': zipcode_info.major_city,
            'state': zipcode_info.state
        }, None
```

#### 错误处理与备用方案
当uszipcode没有时区数据时，可使用备用方案：
```python
# 备用方案：通过经纬度查询时区
from timezonefinder import TimezoneFinder

if not timezone_name and zipcode_info.lat and zipcode_info.lng:
    tf = TimezoneFinder()
    timezone_name = tf.timezone_at(lat=zipcode_info.lat, lng=zipcode_info.lng)
```

#### 性能优化
1. **数据缓存**：
   - 缓存最近查询的ZIP码结果
   - 复用pytzwhere实例，避免重复加载
   
2. **异步处理**：
   - 使用线程处理查询，避免GUI冻结
   - 显示加载进度指示器

3. **内存管理**：
   - 合理控制缓存大小
   - 及时释放不必要的对象

### 6.3 开发环境配置（简化版）

#### 核心依赖安装
```bash
# 主要依赖（只需两个库）
pip install uszipcode  # ZIP码时区查询
pip install pytz       # 时区时间处理

# 可选备用库
pip install timezonefinder  # 仅在uszipcode无时区数据时使用
```

#### 打包配置（简化版）
```bash
# PyInstaller打包命令
pyinstaller --onefile --windowed \
  --add-data "path/to/uszipcode/data;uszipcode/data" \
  --hidden-import=uszipcode \
  --hidden-import=pytz \
  main.py
```

#### 开发优势
1. **依赖最小化**：主要只需2个库，大幅减少复杂性
2. **启动速度**：无需加载大型时区边界文件
3. **维护简单**：uszipcode活跃维护，pytz是标准库
4. **调试容易**：查询链路简单，便于问题定位

## 7. 交付标准

### 7.1 最终交付物
1. **可执行文件**：ZipTimezone.exe
2. **用户说明**：简单的使用说明文档
3. **版本信息**：包含版本号和开发日期

### 7.2 验收标准
- 在全新的Windows系统上能够直接运行
- 所有核心功能正常工作
- 界面友好，操作直观
- 查询响应快速准确
- 错误处理得当，不会造成程序崩溃

## 8. 风险与应对

### 8.1 潜在风险
1. **数据准确性风险**：ZIP码边界变更或时区调整
2. **兼容性风险**：不同Windows版本的兼容问题
3. **性能风险**：大数据量查询造成的性能问题

### 8.2 应对措施
1. 使用最新的官方ZIP码数据库
2. 广泛的兼容性测试
3. 优化数据查询算法，使用索引加速

## 9. 未来扩展可能

### 9.1 功能扩展
- 支持其他国家的邮政编码查询
- 添加世界时钟功能
- 支持时区转换计算

### 9.2 技术扩展
- 增加自动更新功能
- 添加用户偏好设置
- 支持多语言界面

---

**文档版本**：1.0  
**创建日期**：2025年5月18日  
**最后更新**：2025年5月18日