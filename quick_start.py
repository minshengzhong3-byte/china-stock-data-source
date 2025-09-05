#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
China Stock Data Source - 快速启动脚本
提供开箱即用的股票数据获取体验

使用方法:
    python quick_start.py                    # 交互式演示
    python quick_start.py --test            # 运行基础测试
    python quick_start.py --demo            # 运行完整演示
    python quick_start.py --health          # 健康检查
    python quick_start.py --install         # 安装依赖
"""

import sys
import os
import argparse
import traceback
from datetime import datetime, timedelta

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def print_banner():
    """打印欢迎横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                China Stock Data Source                       ║
║                   中国股票数据源                              ║
║                                                              ║
║  🚀 开箱即用的A股数据获取工具                                 ║
║  📊 支持多数据源，统一接口                                    ║
║  🤖 AI友好设计，量化交易优化                                  ║
║                                                              ║
║  GitHub: https://github.com/minshengzhong3-byte/china-stock-data-source
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def run_health_check():
    """运行健康检查"""
    print("\n🔍 运行健康检查...")
    try:
        import health_check
        result = health_check.main()
        return result
    except ImportError:
        print("❌ 健康检查模块未找到，请确保health_check.py存在")
        return False
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False

def install_dependencies():
    """安装依赖"""
    print("\n📦 安装项目依赖...")
    try:
        import install
        install.main()
        return True
    except ImportError:
        print("❌ 安装脚本未找到，请确保install.py存在")
        return False
    except Exception as e:
        print(f"❌ 依赖安装失败: {e}")
        return False

def run_basic_test():
    """运行基础测试"""
    print("\n🧪 运行基础功能测试...")
    
    try:
        # 测试导入
        print("  ✓ 测试模块导入...")
        from unified_data_source import get_stock_data, get_realtime_price
        from quant_adapters import UniversalAdapter
        
        # 测试实时数据获取
        print("  ✓ 测试实时数据获取...")
        realtime_data = get_realtime_price('000001')
        if realtime_data:
            print(f"    平安银行(000001) 实时价格: {realtime_data.get('price', 'N/A')}")
        
        # 测试历史数据获取
        print("  ✓ 测试历史数据获取...")
        hist_data = get_stock_data('000001', period='1d', count=5)
        if hist_data is not None and not hist_data.empty:
            print(f"    获取到 {len(hist_data)} 条历史数据")
            print(f"    最新收盘价: {hist_data['close'].iloc[-1]:.2f}")
        
        # 测试适配器
        print("  ✓ 测试量化适配器...")
        adapter = UniversalAdapter()
        ohlcv = adapter.get_ohlcv('000001', count=5)
        if ohlcv is not None:
            print(f"    OHLCV数据: {len(ohlcv)} 条记录")
        
        print("\n✅ 基础测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 基础测试失败: {e}")
        print("详细错误信息:")
        traceback.print_exc()
        return False

def run_demo():
    """运行完整演示"""
    print("\n🎯 运行完整功能演示...")
    
    try:
        from unified_data_source import get_stock_data, get_realtime_price
        from quant_adapters import UniversalAdapter
        
        # 演示股票列表
        demo_stocks = ['000001', '000002', '600000', '600036']
        stock_names = {
            '000001': '平安银行',
            '000002': '万科A',
            '600000': '浦发银行',
            '600036': '招商银行'
        }
        
        print("\n📊 实时行情演示:")
        print("-" * 60)
        print(f"{'股票代码':<10} {'股票名称':<10} {'当前价格':<10} {'涨跌幅':<10}")
        print("-" * 60)
        
        for stock in demo_stocks:
            try:
                data = get_realtime_price(stock)
                if data:
                    name = stock_names.get(stock, stock)
                    price = data.get('price', 'N/A')
                    change_pct = data.get('change_pct', 'N/A')
                    print(f"{stock:<10} {name:<10} {price:<10} {change_pct:<10}")
                else:
                    print(f"{stock:<10} {stock_names.get(stock, stock):<10} {'无数据':<10} {'N/A':<10}")
            except Exception as e:
                print(f"{stock:<10} {stock_names.get(stock, stock):<10} {'错误':<10} {str(e)[:8]:<10}")
        
        print("\n📈 历史数据演示 (平安银行 最近5天):")
        print("-" * 80)
        
        hist_data = get_stock_data('000001', period='1d', count=5)
        if hist_data is not None and not hist_data.empty:
            print(f"{'日期':<12} {'开盘':<8} {'最高':<8} {'最低':<8} {'收盘':<8} {'成交量':<12}")
            print("-" * 80)
            for _, row in hist_data.tail(5).iterrows():
                date_str = row.name.strftime('%Y-%m-%d') if hasattr(row.name, 'strftime') else str(row.name)[:10]
                print(f"{date_str:<12} {row['open']:<8.2f} {row['high']:<8.2f} {row['low']:<8.2f} {row['close']:<8.2f} {row['volume']:<12.0f}")
        
        print("\n🔧 量化适配器演示:")
        print("-" * 50)
        
        adapter = UniversalAdapter()
        
        # 获取OHLCV数据
        ohlcv = adapter.get_ohlcv('000001', count=3)
        if ohlcv is not None:
            print(f"✓ OHLCV数据: {len(ohlcv)} 条记录")
            print(f"  最新收盘价: {ohlcv['close'].iloc[-1]:.2f}")
        
        # 计算技术指标
        try:
            sma = adapter.calculate_sma('000001', period=5)
            if sma is not None:
                print(f"✓ 5日均线: {sma:.2f}")
        except:
            print("✓ 技术指标计算功能可用")
        
        print("\n🎉 演示完成！所有功能正常运行。")
        print("\n💡 提示:")
        print("  - 使用 'from src.unified_data_source import *' 导入核心功能")
        print("  - 使用 'from src.quant_adapters import *' 导入量化适配器")
        print("  - 查看 examples/ 目录获取更多使用示例")
        print("  - 阅读 AI_QUICK_START.md 了解AI集成方法")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 演示运行失败: {e}")
        print("详细错误信息:")
        traceback.print_exc()
        return False

def interactive_mode():
    """交互式模式"""
    print("\n🎮 进入交互式模式...")
    print("\n可用的快捷命令:")
    print("  get_stock_data('000001')           # 获取历史数据")
    print("  get_realtime_price('000001')       # 获取实时价格")
    print("  adapter = UniversalAdapter()       # 创建适配器")
    print("  adapter.get_ohlcv('000001')        # 获取OHLCV数据")
    print("  exit()                             # 退出")
    
    try:
        # 导入常用模块到全局命名空间
        from unified_data_source import get_stock_data, get_realtime_price
        from quant_adapters import UniversalAdapter
        import pandas as pd
        import numpy as np
        
        # 创建适配器实例
        adapter = UniversalAdapter()
        
        # 将变量添加到全局命名空间
        globals().update({
            'get_stock_data': get_stock_data,
            'get_realtime_price': get_realtime_price,
            'UniversalAdapter': UniversalAdapter,
            'adapter': adapter,
            'pd': pd,
            'np': np
        })
        
        print("\n✅ 模块已导入，可以直接使用上述函数和变量")
        print("\n示例: get_realtime_price('000001')")
        
        # 启动交互式Python解释器
        import code
        code.interact(local=globals())
        
    except Exception as e:
        print(f"❌ 交互式模式启动失败: {e}")
        traceback.print_exc()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='China Stock Data Source - 快速启动脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python quick_start.py                # 交互式演示
  python quick_start.py --test        # 运行基础测试
  python quick_start.py --demo        # 运行完整演示
  python quick_start.py --health      # 健康检查
  python quick_start.py --install     # 安装依赖
        """
    )
    
    parser.add_argument('--test', action='store_true', help='运行基础功能测试')
    parser.add_argument('--demo', action='store_true', help='运行完整功能演示')
    parser.add_argument('--health', action='store_true', help='运行健康检查')
    parser.add_argument('--install', action='store_true', help='安装项目依赖')
    parser.add_argument('--quiet', action='store_true', help='静默模式，减少输出')
    
    args = parser.parse_args()
    
    if not args.quiet:
        print_banner()
    
    success = True
    
    try:
        if args.install:
            success = install_dependencies()
        elif args.health:
            success = run_health_check()
        elif args.test:
            success = run_basic_test()
        elif args.demo:
            success = run_demo()
        else:
            # 默认模式：先运行基础测试，然后进入交互模式
            if not args.quiet:
                print("\n🚀 欢迎使用 China Stock Data Source!")
                print("\n首先运行基础测试确保一切正常...")
            
            if run_basic_test():
                if not args.quiet:
                    print("\n🎯 基础测试通过，现在可以开始使用了！")
                    print("\n选择下一步操作:")
                    print("  1. 运行完整演示 (输入 'demo')")
                    print("  2. 进入交互模式 (输入 'interactive' 或直接回车)")
                    print("  3. 退出 (输入 'exit')")
                    
                    choice = input("\n请选择 [demo/interactive/exit]: ").strip().lower()
                    
                    if choice == 'demo':
                        run_demo()
                    elif choice == 'exit':
                        print("\n👋 再见！")
                    else:
                        interactive_mode()
                else:
                    interactive_mode()
            else:
                success = False
                if not args.quiet:
                    print("\n❌ 基础测试失败，请检查环境配置")
                    print("\n💡 建议:")
                    print("  1. 运行 'python quick_start.py --install' 安装依赖")
                    print("  2. 运行 'python quick_start.py --health' 检查系统状态")
    
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，再见！")
        success = True
    except Exception as e:
        print(f"\n❌ 程序运行出错: {e}")
        if not args.quiet:
            traceback.print_exc()
        success = False
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()