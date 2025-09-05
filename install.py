#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
China Stock Data Source 一键安装脚本

自动检测环境并安装所有必要依赖，确保开箱即用体验。

使用方法:
    python install.py
    python install.py --check-only  # 仅检查环境
    python install.py --force       # 强制重新安装
"""

import sys
import subprocess
import importlib
import argparse
import os
from pathlib import Path

# 必需依赖列表
REQUIRED_PACKAGES = {
    'pandas': '>=1.3.0',
    'numpy': '>=1.20.0',
    'requests': '>=2.25.0',
    'beautifulsoup4': '>=4.9.0',
    'lxml': '>=4.6.0',
}

# 可选依赖（用于增强功能）
OPTIONAL_PACKAGES = {
    'akshare': '>=1.8.0',
    'tushare': '>=1.2.0',
    'yfinance': '>=0.1.70',
    'matplotlib': '>=3.3.0',
    'seaborn': '>=0.11.0',
}

# 量化框架适配依赖
QUANT_PACKAGES = {
    'backtrader': '>=1.9.76',
    'zipline': '>=2.2.0',
    'vnpy': '>=3.0.0',
}

class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_colored(text, color=Colors.END):
    """打印彩色文本"""
    print(f"{color}{text}{Colors.END}")

def check_python_version():
    """检查Python版本"""
    print_colored("🐍 检查Python版本...", Colors.BLUE)
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print_colored(f"❌ Python版本过低: {version.major}.{version.minor}", Colors.RED)
        print_colored("   需要Python 3.7或更高版本", Colors.RED)
        return False
    
    print_colored(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}", Colors.GREEN)
    return True

def check_package(package_name, version_req=None):
    """检查包是否已安装"""
    try:
        module = importlib.import_module(package_name)
        if hasattr(module, '__version__'):
            version = module.__version__
            print_colored(f"✅ {package_name}: {version}", Colors.GREEN)
            return True
        else:
            print_colored(f"✅ {package_name}: 已安装", Colors.GREEN)
            return True
    except ImportError:
        print_colored(f"❌ {package_name}: 未安装", Colors.RED)
        return False

def install_package(package_name, version_req=None):
    """安装包"""
    try:
        if version_req:
            package_spec = f"{package_name}{version_req}"
        else:
            package_spec = package_name
        
        print_colored(f"📦 安装 {package_spec}...", Colors.YELLOW)
        
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', package_spec],
            capture_output=True,
            text=True,
            check=True
        )
        
        print_colored(f"✅ {package_name} 安装成功", Colors.GREEN)
        return True
        
    except subprocess.CalledProcessError as e:
        print_colored(f"❌ {package_name} 安装失败: {e}", Colors.RED)
        print_colored(f"   错误输出: {e.stderr}", Colors.RED)
        return False

def check_network_connectivity():
    """检查网络连接"""
    print_colored("🌐 检查网络连接...", Colors.BLUE)
    
    test_urls = [
        'https://pypi.org',
        'https://mirrors.aliyun.com',
        'https://www.baidu.com'
    ]
    
    import requests
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print_colored(f"✅ 网络连接正常: {url}", Colors.GREEN)
                return True
        except:
            continue
    
    print_colored("❌ 网络连接异常，可能影响包安装", Colors.RED)
    return False

def setup_pip_mirror():
    """设置pip镜像源"""
    print_colored("🔧 配置pip镜像源...", Colors.BLUE)
    
    pip_conf_dir = Path.home() / '.pip'
    pip_conf_dir.mkdir(exist_ok=True)
    
    pip_conf_file = pip_conf_dir / 'pip.conf'
    
    config_content = """
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
trusted-host = mirrors.aliyun.com
"""
    
    try:
        with open(pip_conf_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        print_colored("✅ pip镜像源配置完成", Colors.GREEN)
        return True
    except Exception as e:
        print_colored(f"⚠️ pip镜像源配置失败: {e}", Colors.YELLOW)
        return False

def test_data_source():
    """测试数据源连接"""
    print_colored("🧪 测试数据源连接...", Colors.BLUE)
    
    try:
        # 导入并测试数据源
        sys.path.insert(0, str(Path(__file__).parent / 'src'))
        
        from unified_data_source import get_realtime_price, UnifiedDataSource
        
        # 创建数据源实例
        ds = UnifiedDataSource(timeout=10)
        
        # 测试获取实时价格
        test_symbol = '000001'
        print_colored(f"   测试获取 {test_symbol} 实时价格...", Colors.YELLOW)
        
        price_data = ds.get_realtime_price(test_symbol)
        
        if price_data and 'current_price' in price_data:
            print_colored(f"✅ 数据源连接正常: {test_symbol} = {price_data['current_price']}", Colors.GREEN)
            return True
        else:
            print_colored("❌ 数据源返回数据异常", Colors.RED)
            return False
            
    except Exception as e:
        print_colored(f"❌ 数据源测试失败: {e}", Colors.RED)
        return False

def create_quick_start_script():
    """创建快速启动脚本"""
    print_colored("📝 创建快速启动脚本...", Colors.BLUE)
    
    script_content = '''
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速启动脚本 - 验证安装并运行基本示例
"""

import sys
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from unified_data_source import get_stock_data, get_realtime_price
    
    print("🚀 China Stock Data Source 快速启动测试")
    print("=" * 50)
    
    # 测试实时价格获取
    print("📊 获取实时价格...")
    price = get_realtime_price('000001')
    print(f"平安银行(000001): {price['current_price']} 元")
    
    # 测试历史数据获取
    print("\n📈 获取历史数据...")
    data = get_stock_data('000001', period='1w')
    print(f"获取到 {len(data)} 条历史数据")
    print(data.tail())
    
    print("\n✅ 所有测试通过！数据源工作正常。")
    print("\n📖 更多使用方法请参考:")
    print("   - README.md")
    print("   - AI_QUICK_START.md")
    print("   - examples/ 目录下的示例")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    print("\n🔧 故障排除:")
    print("   1. 检查网络连接")
    print("   2. 运行: python install.py")
    print("   3. 查看 README.md 中的故障排除部分")
    sys.exit(1)
'''
    
    try:
        with open('quick_start.py', 'w', encoding='utf-8') as f:
            f.write(script_content)
        print_colored("✅ 快速启动脚本创建完成: quick_start.py", Colors.GREEN)
        return True
    except Exception as e:
        print_colored(f"❌ 快速启动脚本创建失败: {e}", Colors.RED)
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='China Stock Data Source 安装脚本')
    parser.add_argument('--check-only', action='store_true', help='仅检查环境，不安装')
    parser.add_argument('--force', action='store_true', help='强制重新安装所有包')
    parser.add_argument('--with-quant', action='store_true', help='同时安装量化框架依赖')
    parser.add_argument('--no-test', action='store_true', help='跳过数据源连接测试')
    
    args = parser.parse_args()
    
    print_colored("🎯 China Stock Data Source 安装程序", Colors.BOLD)
    print_colored("=" * 50, Colors.BOLD)
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 设置pip镜像源
    setup_pip_mirror()
    
    # 检查网络连接
    check_network_connectivity()
    
    success_count = 0
    total_count = 0
    
    # 检查和安装必需依赖
    print_colored("\n📦 检查必需依赖...", Colors.BLUE)
    for package, version in REQUIRED_PACKAGES.items():
        total_count += 1
        if args.force or not check_package(package, version):
            if not args.check_only:
                if install_package(package, version):
                    success_count += 1
        else:
            success_count += 1
    
    # 检查和安装可选依赖
    print_colored("\n🔧 检查可选依赖...", Colors.BLUE)
    for package, version in OPTIONAL_PACKAGES.items():
        if not check_package(package, version):
            if not args.check_only:
                print_colored(f"⚠️ 可选依赖 {package} 未安装，建议安装以获得更好体验", Colors.YELLOW)
                user_input = input(f"是否安装 {package}? (y/N): ")
                if user_input.lower() in ['y', 'yes']:
                    install_package(package, version)
    
    # 安装量化框架依赖
    if args.with_quant:
        print_colored("\n🏦 检查量化框架依赖...", Colors.BLUE)
        for package, version in QUANT_PACKAGES.items():
            if not check_package(package, version):
                if not args.check_only:
                    install_package(package, version)
    
    # 创建快速启动脚本
    if not args.check_only:
        create_quick_start_script()
    
    # 测试数据源连接
    if not args.no_test and not args.check_only:
        print_colored("\n🧪 测试数据源...", Colors.BLUE)
        test_success = test_data_source()
    else:
        test_success = True
    
    # 输出结果
    print_colored("\n" + "=" * 50, Colors.BOLD)
    if args.check_only:
        print_colored("✅ 环境检查完成", Colors.GREEN)
    else:
        if success_count == total_count and test_success:
            print_colored("🎉 安装完成！数据源已准备就绪。", Colors.GREEN)
            print_colored("\n🚀 快速开始:", Colors.BOLD)
            print_colored("   python quick_start.py", Colors.BLUE)
            print_colored("\n📖 更多信息:", Colors.BOLD)
            print_colored("   - 查看 README.md", Colors.BLUE)
            print_colored("   - 查看 AI_QUICK_START.md", Colors.BLUE)
            print_colored("   - 运行 examples/ 目录下的示例", Colors.BLUE)
        else:
            print_colored("⚠️ 安装过程中遇到问题，请检查错误信息", Colors.YELLOW)
            print_colored("\n🔧 故障排除:", Colors.BOLD)
            print_colored("   1. 检查网络连接", Colors.BLUE)
            print_colored("   2. 尝试使用管理员权限运行", Colors.BLUE)
            print_colored("   3. 查看 README.md 中的故障排除部分", Colors.BLUE)

if __name__ == '__main__':
    main()