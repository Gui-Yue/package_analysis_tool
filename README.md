# Debian Package Dependency Analyzer

这是一个用于分析 Debian trixie 源码包依赖关系的 Python 工具。

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

## 使用方法

### 交互式输入

1. **输入目标包名**: 输入要分析的软件包名称，多个包名用逗号分隔
   ```
   请输入要分析的目标包名（用逗号分隔）: qt6-webengine-dev,qtwebengine5-dev
   ```

2. **选择过滤选项**: 选择是否过滤纯 `all` 架构的软件包
   ```
   是否过滤纯all包？(yes/no，默认yes): yes
   ```

## 输出结果

### 1. 控制台输出
- 初始化环境信息
- 每个目标包的依赖分析进度
- 找到的依赖包数量
- 详细的依赖链条信息
- 最终的综合结果统计

### 2. Excel 文件
脚本会在 `result/` 目录下生成带时间戳的 Excel 文件，包含以下列：

| 列名 | 说明 |
|------|------|
| 包名 | 依赖包的名称 |
| 分类 | 软件包的分类（如 devel, libs 等） |
| 架构 | 支持的架构（如 any, amd64, all 等） |
| 主页 | 软件包的官方主页 |
| 依赖链条 | 完整的依赖路径，多条路径用逗号分隔 |

## 目录结构

```
package_dependency_analysis/
├── package_dependency_analyzer.py  # 主脚本
├── requirements.txt                # Python 依赖包列表
├── venv/                           # Python 虚拟环境（用户创建）
├── result/                         # 输出目录（运行时自动创建）
│   ├── Sources                     # 下载的源码包信息文件
│   └── dependency_analysis_*.xlsx  # 生成的 Excel 报告
├── .gitignore                      # Git 忽略文件
└── README.md                       # 本说明文件
```

## 主要功能说明

### 初始化环境
- 自动删除并重建 `result` 目录
- 从中科大镜像源下载最新的 debian-trixie Sources.xz 文件
- 解压并准备分析环境

### 依赖分析
- 分析指定软件包的所有直接和间接依赖关系
- 支持过滤纯 `all` 架构的软件包
- 自动合并重复包的依赖链条

### Excel 导出
- 自动生成格式化的 Excel 报告
- 包含完整的包信息和依赖链条
- 支持多条依赖路径的显示

## 注意事项

1. **网络连接**: 首次运行需要下载约 50MB 的 Sources.xz 文件
2. **分析时间**: 依赖包较多时分析可能需要几分钟时间
3. **递归深度**: 为避免无限递归，设置了最大深度限制（10层）
4. **文件权限**: 如果遇到权限问题，运行 `chmod +x package_dependency_analyzer.py`

## 示例运行

```bash
$ source venv/bin/activate
$ python3 package_dependency_analyzer.py 
INFO: Initializing environment...
INFO: Downloading https://mirrors.ustc.edu.cn/debian/dists/trixie/main/source/Sources.xz...
INFO: Extracting Sources.xz...
INFO: Environment initialization completed.
请输入要分析的目标包名（用逗号分隔）: qt6-webengine-dev,qtwebengine5-dev
是否过滤纯all包？(yes/no，默认yes): 

分析目标包: qt6-webengine-dev
==================================================
INFO: Analyzing packages that depend on 'qt6-webengine-dev'...
INFO: filter pure all packages
INFO: 有49个软件包依赖于qt6-webengine-dev
INFO: Analyzing packages that depend on 'akregator'...
INFO: filter pure all packages
INFO: 有0个软件包依赖于akregator
INFO: Analyzing packages that depend on 'angelfish'...
INFO: filter pure all packages
INFO: 有0个软件包依赖于angelfish
INFO: Analyzing packages that depend on 'apvlv'...
INFO: filter pure all packages
INFO: 有0个软件包依赖于apvlv
INFO: Analyzing packages that depend on 'arianna'...
INFO: filter pure all packages
INFO: 有0个软件包依赖于arianna
INFO: Analyzing packages that depend on 'cantor'...
  ...

开始合并结果...
正在获取包的详细信息...

分析完成！
共分析了 2 个目标包
找到 85 个唯一的依赖包

综合结果:
================================================================================
包名: akregator
  分类: misc
  架构: amd64 arm64 armhf i386
  主页: https://invent.kde.org/pim/akregator
  依赖链: qt6-webengine-dev -> akregator
----------------------------------------
包名: angelfish
  分类: misc
  架构: any
  主页: https://apps.kde.org/angelfish/
  依赖链: qt6-webengine-dev -> angelfish

  ... 

正在导出结果到Excel...
Excel文件已保存到: result/dependency_analysis_qt6-webengine-dev_qtwebengine5-dev_20250913_105841.xlsx
```

## 其他说明
- 使用中科大镜像源确保国内用户的下载速度