#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
China Stock Data Source 健康检查工具

全面检查系统状态，诊断连接问题，提供解决方案。

使用方法:
    python health_check.py
    python health_check.py --verbose    # 详细输出
    python health_check.py --fix        # 自动修复问题
    python health_check.py --export     # 导出诊断报告
"""

import sys
import os
import time
import json
import argparse
import traceback
from pathlib import Path
from datetime import datetime
import requests
import subprocess

class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    BOLD = '\033[1m'
    END = '\033[0m'

class HealthChecker:
    """健康检查器"""
    
    def __init__(self, verbose=False, auto_fix=False):
        self.verbose = verbose
        self.auto_fix = auto_fix
        self.results = []
        self.start_time = datetime.now()
        
        # 添加src目录到路径
        src_path = Path(__file__).parent / 'src'
        if src_path.exists():
            sys.path.insert(0, str(src_path))
    
    def log(self, message, color=Colors.END, level='INFO'):
        """记录日志"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        if self.verbose or level in ['ERROR', 'WARNING']:
            print(f"{color}[{timestamp}] {level}: {message}{Colors.END}")
        
        self.results.append({
            'timestamp': timestamp,
            'level': level,
            'message': message
        })
    
    def check_python_environment(self):
        """检查Python环境"""
        self.log("🐍 检查Python环境...", Colors.BLUE)
        
        try:
            # Python版本
            version = sys.version_info
            if version.major >= 3 and version.minor >= 7:
                self.log(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}", Colors.GREEN)
                return True
            else:
                self.log(f"❌ Python版本过低: {version.major}.{version.minor}", Colors.RED, 'ERROR')
                return False
                
        except Exception as e:
            self.log(f"❌ Python环境检查失败: {e}", Colors.RED, 'ERROR')
            return False
    
    def check_dependencies(self):
        """检查依赖包"""
        self.log("📦 检查依赖包...", Colors.BLUE)
        
        required_packages = {
            'pandas': 'pandas',
            'numpy': 'numpy', 
            'requests': 'requests',
            'beautifulsoup4': 'bs4',
            'lxml': 'lxml'
        }
        
        missing_packages = []
        
        for package_name, import_name in required_packages.items():
            try:
                __import__(import_name)
                self.log(f"✅ {package_name}: 已安装", Colors.GREEN)
            except ImportError:
                self.log(f"❌ {package_name}: 未安装", Colors.RED, 'ERROR')
                missing_packages.append(package_name)
        
        if missing_packages:
            self.log(f"缺少依赖: {', '.join(missing_packages)}", Colors.RED, 'ERROR')
            if self.auto_fix:
                self.log("🔧 尝试自动安装缺少的依赖...", Colors.YELLOW)
                for package in missing_packages:
                    try:
                        subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                                     check=True, capture_output=True)
                        self.log(f"✅ {package} 安装成功", Colors.GREEN)
                    except subprocess.CalledProcessError as e:
                        self.log(f"❌ {package} 安装失败: {e}", Colors.RED, 'ERROR')
            return False
        
        return True
    
    def check_network_connectivity(self):
        """检查网络连接"""
        self.log("🌐 检查网络连接...", Colors.BLUE)
        
        test_urls = [
            ('百度', 'https://www.baidu.com'),
            ('新浪财经', 'https://finance.sina.com.cn'),
            ('东方财富', 'https://www.eastmoney.com'),
            ('腾讯财经', 'https://finance.qq.com'),
        ]
        
        success_count = 0
        
        for name, url in test_urls:
            try:
                response = requests.get(url, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                if response.status_code == 200:
                    self.log(f"✅ {name}: 连接正常 ({response.status_code})", Colors.GREEN)
                    success_count += 1
                else:
                    self.log(f"⚠️ {name}: 状态码 {response.status_code}", Colors.YELLOW, 'WARNING')
                    
            except requests.exceptions.Timeout:
                self.log(f"❌ {name}: 连接超时", Colors.RED, 'ERROR')
            except requests.exceptions.ConnectionError:
                self.log(f"❌ {name}: 连接错误", Colors.RED, 'ERROR')
            except Exception as e:
                self.log(f"❌ {name}: {str(e)}", Colors.RED, 'ERROR')
        
        if success_count >= len(test_urls) // 2:
            self.log(f"✅ 网络连接正常 ({success_count}/{len(test_urls)})", Colors.GREEN)
            return True
        else:
            self.log(f"❌ 网络连接异常 ({success_count}/{len(test_urls)})", Colors.RED, 'ERROR')
            return False
    
    def check_data_sources(self):
        """检查数据源连接"""
        self.log("📊 检查数据源连接...", Colors.BLUE)
        
        try:
            from unified_data_source import UnifiedDataSource
            
            # 创建数据源实例
            ds = UnifiedDataSource(timeout=15)
            
            # 测试股票列表
            test_stocks = ['000001', '000002', '600000', '600036']
            success_count = 0
            
            for stock_code in test_stocks:
                try:
                    self.log(f"   测试 {stock_code}...", Colors.YELLOW)
                    
                    # 测试实时价格
                    price_data = ds.get_realtime_price(stock_code)
                    
                    if price_data and 'current_price' in price_data:
                        price = price_data['current_price']
                        change = price_data.get('change_percent', 'N/A')
                        self.log(f"✅ {stock_code}: {price}元 ({change}%)", Colors.GREEN)
                        success_count += 1
                    else:
                        self.log(f"❌ {stock_code}: 数据格式异常", Colors.RED, 'ERROR')
                        
                except Exception as e:
                    self.log(f"❌ {stock_code}: {str(e)}", Colors.RED, 'ERROR')
                    
                # 避免请求过于频繁
                time.sleep(1)
            
            if success_count >= len(test_stocks) // 2:
                self.log(f"✅ 数据源连接正常 ({success_count}/{len(test_stocks)})", Colors.GREEN)
                return True
            else:
                self.log(f"❌ 数据源连接异常 ({success_count}/{len(test_stocks)})", Colors.RED, 'ERROR')
                return False
                
        except ImportError as e:
            self.log(f"❌ 无法导入数据源模块: {e}", Colors.RED, 'ERROR')
            return False
        except Exception as e:
            self.log(f"❌ 数据源检查失败: {e}", Colors.RED, 'ERROR')
            if self.verbose:
                self.log(f"详细错误: {traceback.format_exc()}", Colors.RED, 'ERROR')
            return False
    
    def check_performance(self):
        """检查性能指标"""
        self.log("⚡ 检查性能指标...", Colors.BLUE)
        
        try:
            from unified_data_source import get_realtime_price
            
            # 测试响应时间
            test_stock = '000001'
            start_time = time.time()
            
            result = get_realtime_price(test_stock)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # 转换为毫秒
            
            if result:
                if response_time < 2000:  # 2秒内
                    self.log(f"✅ 响应时间: {response_time:.0f}ms (优秀)", Colors.GREEN)
                    return True
                elif response_time < 5000:  # 5秒内
                    self.log(f"⚠️ 响应时间: {response_time:.0f}ms (一般)", Colors.YELLOW, 'WARNING')
                    return True
                else:
                    self.log(f"❌ 响应时间: {response_time:.0f}ms (过慢)", Colors.RED, 'ERROR')
                    return False
            else:
                self.log("❌ 性能测试失败: 无法获取数据", Colors.RED, 'ERROR')
                return False
                
        except Exception as e:
            self.log(f"❌ 性能检查失败: {e}", Colors.RED, 'ERROR')
            return False
    
    def check_file_structure(self):
        """检查文件结构"""
        self.log("📁 检查文件结构...", Colors.BLUE)
        
        required_files = [
            'src/__init__.py',
            'src/unified_data_source.py',
            'src/abu_source.py', 
            'src/ashare_source.py',
            'README.md',
            'requirements.txt'
        ]
        
        missing_files = []
        
        for file_path in required_files:
            full_path = Path(__file__).parent / file_path
            if full_path.exists():
                self.log(f"✅ {file_path}: 存在", Colors.GREEN)
            else:
                self.log(f"❌ {file_path}: 缺失", Colors.RED, 'ERROR')
                missing_files.append(file_path)
        
        if missing_files:
            self.log(f"缺少文件: {', '.join(missing_files)}", Colors.RED, 'ERROR')
            return False
        
        return True
    
    def generate_diagnostic_report(self):
        """生成诊断报告"""
        report = {
            'timestamp': self.start_time.isoformat(),
            'duration': (datetime.now() - self.start_time).total_seconds(),
            'system_info': {
                'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                'platform': sys.platform,
                'cwd': str(Path.cwd())
            },
            'results': self.results
        }
        
        return report
    
    def export_report(self, filename=None):
        """导出诊断报告"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'health_check_report_{timestamp}.json'
        
        report = self.generate_diagnostic_report()
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            self.log(f"📄 诊断报告已导出: {filename}", Colors.GREEN)
            return filename
            
        except Exception as e:
            self.log(f"❌ 报告导出失败: {e}", Colors.RED, 'ERROR')
            return None
    
    def provide_solutions(self, failed_checks):
        """提供解决方案"""
        if not failed_checks:
            return
        
        self.log("\n🔧 故障排除建议:", Colors.BOLD)
        
        solutions = {
            'python_environment': [
                "升级Python到3.7或更高版本",
                "检查Python安装是否完整"
            ],
            'dependencies': [
                "运行: pip install -r requirements.txt",
                "运行: python install.py",
                "检查pip是否正常工作"
            ],
            'network_connectivity': [
                "检查网络连接",
                "检查防火墙设置",
                "尝试使用VPN或代理",
                "检查DNS设置"
            ],
            'data_sources': [
                "检查网络连接到财经网站",
                "等待一段时间后重试（可能是临时限制）",
                "检查是否需要更新数据源配置",
                "尝试使用不同的数据源"
            ],
            'performance': [
                "检查网络速度",
                "关闭其他占用网络的程序",
                "尝试在网络较好的时间段使用"
            ],
            'file_structure': [
                "重新下载完整的项目文件",
                "检查文件是否被意外删除",
                "从GitHub重新克隆项目"
            ]
        }
        
        for check_name in failed_checks:
            if check_name in solutions:
                self.log(f"\n{check_name.replace('_', ' ').title()}:", Colors.YELLOW)
                for i, solution in enumerate(solutions[check_name], 1):
                    self.log(f"  {i}. {solution}", Colors.BLUE)
    
    def run_all_checks(self):
        """运行所有检查"""
        self.log("🎯 开始健康检查...", Colors.BOLD)
        self.log("=" * 60, Colors.BOLD)
        
        checks = [
            ('python_environment', self.check_python_environment),
            ('file_structure', self.check_file_structure),
            ('dependencies', self.check_dependencies),
            ('network_connectivity', self.check_network_connectivity),
            ('data_sources', self.check_data_sources),
            ('performance', self.check_performance)
        ]
        
        passed_checks = []
        failed_checks = []
        
        for check_name, check_func in checks:
            try:
                if check_func():
                    passed_checks.append(check_name)
                else:
                    failed_checks.append(check_name)
            except Exception as e:
                self.log(f"❌ {check_name} 检查异常: {e}", Colors.RED, 'ERROR')
                failed_checks.append(check_name)
            
            self.log("")  # 空行分隔
        
        # 输出总结
        self.log("=" * 60, Colors.BOLD)
        total_checks = len(checks)
        passed_count = len(passed_checks)
        
        if passed_count == total_checks:
            self.log(f"🎉 所有检查通过! ({passed_count}/{total_checks})", Colors.GREEN)
            self.log("✅ 系统状态良好，可以正常使用。", Colors.GREEN)
        else:
            self.log(f"⚠️ 检查完成: {passed_count}/{total_checks} 通过", Colors.YELLOW)
            self.log(f"❌ 失败的检查: {', '.join(failed_checks)}", Colors.RED)
            
            # 提供解决方案
            self.provide_solutions(failed_checks)
        
        return passed_count == total_checks

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='China Stock Data Source 健康检查工具')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    parser.add_argument('--fix', action='store_true', help='自动修复问题')
    parser.add_argument('--export', action='store_true', help='导出诊断报告')
    parser.add_argument('--output', '-o', help='指定报告输出文件名')
    
    args = parser.parse_args()
    
    # 创建健康检查器
    checker = HealthChecker(verbose=args.verbose, auto_fix=args.fix)
    
    try:
        # 运行所有检查
        success = checker.run_all_checks()
        
        # 导出报告
        if args.export:
            checker.export_report(args.output)
        
        # 返回适当的退出码
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        checker.log("\n⚠️ 用户中断检查", Colors.YELLOW)
        sys.exit(1)
    except Exception as e:
        checker.log(f"❌ 检查过程中发生异常: {e}", Colors.RED, 'ERROR')
        if args.verbose:
            checker.log(f"详细错误: {traceback.format_exc()}", Colors.RED, 'ERROR')
        sys.exit(1)

if __name__ == '__main__':
    main()