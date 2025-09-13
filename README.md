# Debian Package Dependency Analyzer

这是一个用于分析 Debian trixie 源码包依赖关系的 Python 工具。支持两种分析模式：**二进制包模式**和**源码包模式**，帮助分析包依赖链条和构建影响。

## 环境要求

- Python 3.13+
- python3-pip
- 网络连接（用于下载 Sources.xz 文件）

## 快速开始

### 1. 创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 运行脚本
```bash
python3 package_dependency_analyzer.py
```

## 分析模式

脚本支持两种分析模式，运行时会提示选择：

### 模式1：二进制包模式
- **输入**：具体的二进制包名（如 `libqt5webengine5`、`python3-pyside2.qtwebengine`）
- **用途**：分析缺少某个特定库或工具会影响哪些源码包的构建
- **依赖链条格式**：`二进制包 -> 源码包1 -> 源码包2 -> ...`

### 模式2：源码包模式 
- **输入**：源码包名（如 `qt6-webengine`、`pyside2`）
- **用途**：分析某个源码包构建成功后能疏通哪些构建阻塞
- **依赖链条格式**：`源码包 -> 受影响源码包1 -> 受影响源码包2 -> ...`
- **特点**：自动遍历源码包的所有二进制包，提供完整的影响分析

## 使用方法

### 模式选择
```
请选择分析模式:
1. 二进制包模式 - 以具体的二进制包为目标
2. 源码包模式 - 以源码包为目标，分析整个源码包的影响

请输入模式编号 (1 或 2, 默认1): 2
```

### 交互式输入

#### 二进制包模式输入示例：
```
请输入要分析的目标二进制包名（用逗号分隔）: libqt5webengine5,python3-numpy
```

#### 源码包模式输入示例：
```
请输入要分析的目标源码包名（用逗号分隔）: qt6-webengine,qtwebengine-opensource-src
```

### 过滤选项
```
是否过滤纯all包？(yes/no，默认yes): yes
```

## 输出结果

### 1. 控制台输出
- 初始化环境信息（下载和解压 Sources.xz）
- 模式选择和目标包输入
- 每个目标包的依赖分析进度
- 源码包级别的依赖链条展示
- 最终的综合结果统计

### 2. Excel 文件
脚本会在 `result/` 目录下生成带时间戳的 Excel 文件，包含以下列：

| 列名 | 说明 |
|------|------|
| 包名 | 受影响源码包的名称 |
| 分类 | 软件包的分类（如 devel, libs 等） |
| 架构 | 支持的架构（如 any, amd64, all 等） |
| 主页 | 软件包的官方主页 |
| 依赖链条 | 完整的依赖路径，多条路径用分号分隔 |

## 目录结构

```
package_dependency_analysis/
├── package_dependency_analyzer.py     # 主脚本
├── requirements.txt                   # Python 依赖包列表
├── venv/                             # Python 虚拟环境（用户创建）
├── result/                           # 输出目录（运行时自动创建）
│   ├── Sources                       # 下载的源码包信息文件
│   └── dependency_analysis_*.xlsx    # 生成的 Excel 报告
├── .gitignore                        # Git 忽略文件
└── README.md                         # 本说明文件
```

## 主要功能说明

### 初始化环境
- 自动删除并重建 `result` 目录
- 从中科大镜像源下载最新的 debian-trixie Sources.xz 文件
- 解压文件并准备分析环境

### 源码包级别依赖分析
- **完整性**：当发现一个源码包依赖关系时，会分析该源码包的所有二进制包
- **递归分析**：深度递归查找间接依赖关系
- **去重合并**：自动合并重复包的依赖链条

### 构建影响分析
- **源码包模式**：分析某个源码包假设构建成功后能影响哪些其他源码包
- **依赖链分析**：帮助理解包之间的依赖关系
- **连锁反应**：展示包依赖的传播路径

### Excel 导出
- 自动生成格式化的 Excel 报告
- 包含完整的源码包信息和依赖链条
- 支持多条依赖路径的显示

## 注意事项

1. **网络连接**：运行需要下载约 50MB 的 Sources.xz 文件
2. **分析时间**：源码包模式可能需要更长时间，特别是分析关键包时
3. **递归深度**：为避免无限递归，设置了最大深度限制
4. **理论分析**：基于 Sources.xz 的依赖关系分析，不涉及实际构建状态

## 示例运行

### 源码包模式示例
```bash
$ cd package_analysis_tool
$ python3 -m venv venv
$ source venv/bin/activate
$ python package_dependency_analyzer.py 
INFO: Initializing environment...
INFO: Downloading https://mirrors.ustc.edu.cn/debian/dists/trixie/main/source/Sources.xz...
INFO: Extracting Sources.xz...
INFO: Environment initialization completed.
请选择分析模式:
1. 二进制包模式 - 以具体的二进制包为目标
2. 源码包模式 - 以源码包为目标，分析整个源码包的影响
请输入模式编号 (1 或 2, 默认1): 
=== 源码包模式 ===
请输入要分析的目标源码包名（用逗号分隔）: 是否过滤纯all包？(yes/no，默认yes): 
分析源码包: qtwebengine-opensource-src,qt6-webengine
==================================================
INFO: 源码包 'qtwebengine-opensource-src' 产生 19 个二进制包: qtwebengine5-dev, qtwebengine5-private-dev, qtpdf5-dev, libqt5webengine5, libqt5webenginecore5, libqt5webenginewidgets5, libqt5pdf5, libqt5pdfwidgets5, libqt5webengine-data, qt5-image-formats-plugin-pdf, qml-module-qtwebengine, qml-module-qtquick-pdf, qtwebengine5-dev-tools, qtwebengine5-examples, qtpdf5-examples, qtwebengine5-doc, qtwebengine5-doc-html, qtpdf5-doc, qtpdf5-doc-html

分析二进制包: qtwebengine5-dev
------------------------------
INFO: 分析依赖于 'qtwebengine5-dev' 的软件包...
INFO: 过滤纯all架构的软件包
INFO: 有37个软件包依赖于qtwebengine5-dev
INFO: 查找依赖于 'qtwebengine5-dev' 的源码包: 找到 37 个
INFO: 源码包 'algobox' 产生 1 个二进制包
INFO: 分析依赖于 'algobox' 的软件包...
INFO: 过滤纯all架构的软件包
INFO: 有0个软件包依赖于algobox
INFO: 查找依赖于 'algobox' 的源码包: 找到 0 个
INFO: 源码包 'amarok' 产生 4 个二进制包
INFO: 分析依赖于 'amarok' 的软件包...
INFO: 过滤纯all架构的软件包

...

分析源码包: qt6-webengine
==================================================
INFO: 源码包 'qt6-webengine' 产生 20 个二进制包: libqt6webenginecore6, libqt6pdf6, libqt6pdfquick6, libqt6pdfwidgets6, libqt6webenginecore6-bin, libqt6webenginequick6, libqt6webenginewidgets6, libqt6webengine6-data, qt6-image-formats-plugin-pdf, qml6-module-qtquick-pdf, qml6-module-qtwebengine, qml6-module-qtwebengine-controlsdelegates, qt6-webengine-dev, qt6-webengine-private-dev, qt6-webengine-dev-tools, qt6-pdf-dev, qt6-webengine-doc, qt6-webengine-doc-html, qt6-webengine-doc-dev, qt6-webengine-examples

分析二进制包: libqt6webenginecore6
------------------------------
INFO: 分析依赖于 'libqt6webenginecore6' 的软件包...
INFO: 过滤纯all架构的软件包
INFO: 有0个软件包依赖于libqt6webenginecore6
INFO: 查找依赖于 'libqt6webenginecore6' 的源码包: 找到 0 个
找到 0 个依赖的源码包

分析二进制包: libqt6pdf6
------------------------------
INFO: 分析依赖于 'libqt6pdf6' 的软件包...
INFO: 过滤纯all架构的软件包
INFO: 有0个软件包依赖于libqt6pdf6
INFO: 查找依赖于 'libqt6pdf6' 的源码包: 找到 0 个
找到 0 个依赖的源码包

...


分析完成！
共分析了 2 个目标源码包
找到 142 个唯一的受影响源码包

源码包依赖结果 (源码包模式):
================================================================================
源码包: algobox
  分类: misc
  架构: any
  主页: https://www.xm1math.net/algobox/
  依赖链条: qtwebengine-opensource-src -> algobox
----------------------------------------
源码包: amarok
  分类: misc
  架构: any all
  主页: https://amarok.kde.org
  依赖链条: qtwebengine-opensource-src -> amarok
----------------------------------------

...

正在导出结果到Excel...
Excel文件已保存到: result/dependency_analysis_qt6-webengine_20250913_161234.xlsx
```

### 二进制包模式示例
```bash
=== 二进制包模式 ===
请输入要分析的目标二进制包名（用逗号分隔）: libqt5webengine5
是否过滤纯all包？(yes/no，默认yes): 

分析目标二进制包: libqt5webengine5
==================================================
INFO: 查找依赖于 'libqt5webengine5' 的源码包: 找到 12 个
找到 12 个依赖的源码包
  pyside2: pyside2
  pyqt5: pyqt5
  qtwebkit: qtwebkit
  ...
```

## 应用场景

### 1. 包构建优先级规划
使用**源码包模式**分析关键包（如编译器、基础库）对其他包的影响范围

### 2. 依赖关系调研
理解 Debian 包生态系统中的依赖关系和传播路径

### 3. 构建影响评估
评估某个包的修改或更新可能影响到的其他包

### 4. 依赖链条追踪
深入分析特定包的完整依赖传播链条


## 其他说明
- 使用中科大镜像源确保国内用户的下载速度
- 支持多目标批量分析
- 自动处理包名映射和依赖解析
- 基于 Build-Depends 和 Build-Depends-Indep 字段进行依赖分析
- 基于官方 Debian trixie Sources.xz 文件
- 源码包级别分析，避免依赖链条缺失  
- 支持控制台显示和 Excel 导出
- 支持二进制包和源码包两种分析模式