#!/home/revy/rv32_deb/investigation_dependency/package_dependency_analysis/venv/bin/python
"""
Debian Package Dependency Analyzer

This script analyzes package dependencies from Debian trixie Sources.xz file.
"""

import os
import shutil
import gzip
import lzma
import urllib.request
import re
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, deque


class PackageDependencyAnalyzer:
    def __init__(self):
        self.result_dir = "result"
        self.sources_file = os.path.join(self.result_dir, "Sources")
        self.sources_url = "https://mirrors.ustc.edu.cn/debian/dists/trixie/main/source/Sources.xz"
    
    def init(self):
        """删除并重建result目录，下载最新的debian-trixie的Source.xz"""
        print("INFO: Initializing environment...")
        
        # 删除并重建result目录
        if os.path.exists(self.result_dir):
            shutil.rmtree(self.result_dir)
        os.makedirs(self.result_dir)
        
        # 下载Sources.xz文件
        sources_xz_path = os.path.join(self.result_dir, "Sources.xz")
        print(f"INFO: Downloading {self.sources_url}...")
        urllib.request.urlretrieve(self.sources_url, sources_xz_path)
        
        # 解压Sources.xz文件
        print("INFO: Extracting Sources.xz...")
        with lzma.open(sources_xz_path, 'rb') as f_in:
            with open(self.sources_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # 删除压缩文件
        os.remove(sources_xz_path)
        print("INFO: Environment initialization completed.")
    
    def _parse_sources_file(self) -> Dict[str, Dict[str, str]]:
        """解析Sources文件，返回包信息字典"""
        packages = {}
        current_package = {}
        current_package_name = None
        
        with open(self.sources_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                if not line:  # 空行，表示一个包的结束
                    if current_package_name and current_package:
                        packages[current_package_name] = current_package.copy()
                    current_package = {}
                    current_package_name = None
                    continue
                
                if line.startswith(' '):  # 继续字段
                    if 'current_field' in locals():
                        current_package[current_field] += ' ' + line.strip()
                    continue
                
                if ':' in line:
                    field, value = line.split(':', 1)
                    field = field.strip()
                    value = value.strip()
                    current_field = field
                    current_package[field] = value
                    
                    if field == 'Package':
                        current_package_name = value
        
        # 处理最后一个包
        if current_package_name and current_package:
            packages[current_package_name] = current_package.copy()
        
        return packages
    
    def _parse_dependencies(self, dep_string: str) -> List[str]:
        """解析依赖字符串，返回包名列表"""
        if not dep_string:
            return []
        
        # 移除版本约束和选择性依赖
        dep_string = re.sub(r'\([^)]*\)', '', dep_string)  # 移除版本约束
        dep_string = re.sub(r'\[[^\]]*\]', '', dep_string)  # 移除架构约束
        
        # 分割依赖项
        deps = []
        for dep in dep_string.split(','):
            # 处理OR依赖（|分隔），只取第一个
            dep = dep.split('|')[0].strip()
            if dep and not dep.startswith('$'):  # 排除变量
                deps.append(dep)
        
        return deps
    
    def analysis(self, target: str, no_all: str = "yes") -> Dict[str, List[str]]:
        """分析依赖于指定target的软件包"""
        print(f"INFO: Analyzing packages that depend on '{target}'...")
        
        if no_all.lower() == "yes":
            print("INFO: filter pure all packages")
        
        packages = self._parse_sources_file()
        result_dict = {}
        
        for pkg_name, pkg_info in packages.items():
            # 检查Build-Depends字段
            build_depends = pkg_info.get('Build-Depends', '')
            build_depends_indep = pkg_info.get('Build-Depends-Indep', '')
            
            all_deps = self._parse_dependencies(build_depends) + self._parse_dependencies(build_depends_indep)
            
            if target in all_deps:
                # 过滤纯all包
                architecture = pkg_info.get('Architecture', '')
                if no_all.lower() == "yes" and architecture == 'all':
                    continue
                
                # 提取包信息
                name = pkg_name
                section = pkg_info.get('Section', 'unknown')
                archs = architecture
                homepage = pkg_info.get('Homepage', '')
                
                result_dict[pkg_name] = [name, section, archs, homepage]
        
        print(f"INFO: 有{len(result_dict)}个软件包依赖于{target}")
        return result_dict
    
    def package_info(self, package_name: str) -> Dict[str, str]:
        """根据包名返回包的详细信息"""
        packages = self._parse_sources_file()
        
        if package_name not in packages:
            return {
                'category': 'unknown',
                'arch': 'unknown', 
                'homepage': ''
            }
        
        pkg_info = packages[package_name]
        return {
            'category': pkg_info.get('Section', 'unknown'),
            'arch': pkg_info.get('Architecture', 'unknown'),
            'homepage': pkg_info.get('Homepage', '')
        }
    
    def export_to_excel(self, comprehensive_result: Dict[str, Dict[str, str]], target_list: List[str]) -> str:
        """将comprehensive_result导出到Excel文件"""
        # 准备数据
        data = []
        for pkg_name, info in comprehensive_result.items():
            data.append({
                '包名': pkg_name,
                '分类': info['category'],
                '架构': info['arch'],
                '主页': info['homepage'],
                '依赖链条': info['dependency_chain']
            })
        
        # 创建DataFrame
        df = pd.DataFrame(data)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_names = "_".join(target_list[:3])  # 最多取前3个目标包名
        if len(target_list) > 3:
            target_names += f"_and_{len(target_list)-3}_more"
        filename = f"dependency_analysis_{target_names}_{timestamp}.xlsx"
        filepath = os.path.join(self.result_dir, filename)
        
        # 导出到Excel
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='依赖分析结果', index=False)
            
            # 获取工作表
            worksheet = writer.sheets['依赖分析结果']
            
            # 调整列宽
            worksheet.column_dimensions['A'].width = 25  # 包名
            worksheet.column_dimensions['B'].width = 20  # 分类
            worksheet.column_dimensions['C'].width = 15  # 架构
            worksheet.column_dimensions['D'].width = 50  # 主页
            worksheet.column_dimensions['E'].width = 80  # 依赖链条
            
            # 设置表头样式
            from openpyxl.styles import Font, PatternFill, Alignment
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            
            for cell in worksheet[1]:
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal="center", vertical="center")
            
            # 设置数据行样式
            for row in worksheet.iter_rows(min_row=2, max_row=len(data)+1):
                for cell in row:
                    cell.alignment = Alignment(vertical="top", wrap_text=True)
        
        return filepath
    
    def _find_all_dependencies(self, target: str, no_all: str, visited: set = None, depth: int = 0, max_depth: int = 10) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
        """递归查找所有直接和间接依赖，返回(依赖包信息, 依赖链条)"""
        if visited is None:
            visited = set()
        
        if depth > max_depth or target in visited:
            return {}, {}
        
        visited.add(target)
        dependency_chain = {target: [target]}
        all_deps = {}
        
        # 查找直接依赖
        direct_deps = self.analysis(target, no_all)
        all_deps.update(direct_deps)
        
        # 为每个直接依赖建立链条
        for dep_name in direct_deps.keys():
            dependency_chain[dep_name] = [target, dep_name]
        
        # 递归查找间接依赖
        for dep_name in list(direct_deps.keys()):
            if dep_name not in visited:
                indirect_deps, indirect_chains = self._find_all_dependencies(dep_name, no_all, visited.copy(), depth + 1, max_depth)
                
                # 合并间接依赖
                all_deps.update(indirect_deps)
                
                # 更新依赖链条
                for indirect_dep, chain in indirect_chains.items():
                    if indirect_dep != dep_name:  # 避免自引用
                        new_chain = [target] + chain
                        dependency_chain[indirect_dep] = new_chain
        
        return all_deps, dependency_chain
    
    def main(self):
        """主流程控制"""
        # 第一步：初始化环境
        self.init()
        
        # 第二步：接收目标包列表
        target_input = input("请输入要分析的目标包名（用逗号分隔）: ").strip()
        target_list = [t.strip() for t in target_input.split(',') if t.strip()]
        
        if not target_list:
            print("ERROR: 未提供有效的目标包名")
            return
        
        # 第三步：接收过滤选项
        filter_input = input("是否过滤纯all包？(yes/no，默认yes): ").strip()
        if not filter_input:
            filter_input = "yes"
        
        # 第四步：分析每个目标包
        final_dep_packages_list = []
        
        for target in target_list:
            print(f"\n分析目标包: {target}")
            print("=" * 50)
            
            # 查找所有依赖（直接和间接）
            all_deps, dependency_chains = self._find_all_dependencies(target, filter_input)
            
            # 构建结果字典
            result = {}
            for pkg_name, chain in dependency_chains.items():
                if pkg_name != target:  # 排除目标包自身
                    result[pkg_name] = chain
            
            final_dep_packages_list.append(result)
            
            print(f"找到 {len(result)} 个依赖包")
            
            # 显示所有结果
            for pkg, chain in result.items():
                print(f"  {pkg}: {' -> '.join(chain)}")
        
        # 第五步：合并所有结果并处理重复包
        print(f"\n开始合并结果...")
        merged_dependencies = {}
        
        for result_dict in final_dep_packages_list:
            for pkg_name, chain in result_dict.items():
                if pkg_name in merged_dependencies:
                    # 如果包已存在，合并依赖链条
                    existing_chains = merged_dependencies[pkg_name]
                    chain_str = ' -> '.join(chain)
                    if chain_str not in existing_chains:
                        existing_chains.append(chain_str)
                else:
                    # 新包，添加依赖链条
                    merged_dependencies[pkg_name] = [' -> '.join(chain)]
        
        # 第六步：生成comprehensive_result
        print(f"正在获取包的详细信息...")
        comprehensive_result = {}
        
        for pkg_name, chains in merged_dependencies.items():
            pkg_info = self.package_info(pkg_name)
            comprehensive_result[pkg_name] = {
                'category': pkg_info['category'],
                'arch': pkg_info['arch'],
                'homepage': pkg_info['homepage'],
                'dependency_chain': ','.join(chains)
            }
        
        # 第七步：输出最终结果
        print(f"\n分析完成！")
        print(f"共分析了 {len(target_list)} 个目标包")
        print(f"找到 {len(comprehensive_result)} 个唯一的依赖包")
        print("\n综合结果:")
        print("=" * 80)
        
        for pkg_name, info in comprehensive_result.items():
            print(f"包名: {pkg_name}")
            print(f"  分类: {info['category']}")
            print(f"  架构: {info['arch']}")
            print(f"  主页: {info['homepage']}")
            print(f"  依赖链: {info['dependency_chain']}")
            print("-" * 40)
        
        # 第八步：导出到Excel
        print(f"\n正在导出结果到Excel...")
        excel_filepath = self.export_to_excel(comprehensive_result, target_list)
        print(f"Excel文件已保存到: {excel_filepath}")
        
        return comprehensive_result


def main():
    """程序入口点"""
    analyzer = PackageDependencyAnalyzer()
    try:
        analyzer.main()
    except KeyboardInterrupt:
        print("\n\nINFO: 用户中断操作")
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    main()