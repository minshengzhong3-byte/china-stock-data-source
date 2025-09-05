# 故障排除指南

本指南帮助您解决使用 China Stock Data Source 时可能遇到的常见问题。

## 🚀 快速诊断

### 一键健康检查
```bash
# 运行完整健康检查
python health_check.py

# 或使用快速启动脚本
python quick_start.py --health
```

### 基础功能测试
```bash
# 测试核心功能
python quick_start.py --test

# 运行完整演示
python quick_start.py --demo
```

## 📋 常见问题分类

### 1. 安装和环境问题

#### 问题：模块导入失败
```
ModuleNotFoundError: No module named 'akshare'
```

**解决方案：**
```bash
# 方法1：使用一键安装脚本
python install.py

# 方法2：手动安装依赖
pip install -r requirements.txt

# 方法3：安装特定模块
pip install akshare tushare yfinance
```

#### 问题：Python版本不兼容
```
SyntaxError: invalid syntax
```

**解决方案：**
- 确保使用 Python 3.7 或更高版本
- 检查Python版本：`python --version`
- 如需要，安装合适的Python版本

#### 问题：网络连接问题
```
ConnectionError: Failed to establish a new connection
```

**解决方案：**
```bash
# 使用国内镜像源
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 或配置pip镜像源
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
```

### 2. 数据获取问题

#### 问题：无法获取股票数据
```
Error: No data found for symbol 000001
```

**诊断步骤：**
1. 检查股票代码格式是否正确
2. 验证网络连接
3. 检查数据源状态

**解决方案：**
```python
# 测试不同数据源
from src.unified_data_source import get_stock_data

# 尝试不同的股票代码
test_symbols = ['000001', '000002', '600000', '600036']
for symbol in test_symbols:
    try:
        data = get_stock_data(symbol, count=5)
        if data is not None:
            print(f"✓ {symbol}: 成功获取 {len(data)} 条数据")
        else:
            print(f"✗ {symbol}: 无数据")
    except Exception as e:
        print(f"✗ {symbol}: 错误 - {e}")
```

#### 问题：数据源连接超时
```
Timeout: The read operation timed out
```

**解决方案：**
```python
# 增加超时时间和重试机制
from src.unified_data_source import UnifiedDataSource

# 创建数据源实例并配置超时
data_source = UnifiedDataSource()
data_source.set_timeout(30)  # 设置30秒超时
data_source.set_retry_count(3)  # 设置重试3次
```

#### 问题：实时数据获取失败
```
Error: Real-time data not available
```

**解决方案：**
```python
# 检查交易时间
from datetime import datetime, time

def is_trading_time():
    now = datetime.now().time()
    # A股交易时间：9:30-11:30, 13:00-15:00
    morning_start = time(9, 30)
    morning_end = time(11, 30)
    afternoon_start = time(13, 0)
    afternoon_end = time(15, 0)
    
    return (morning_start <= now <= morning_end) or (afternoon_start <= now <= afternoon_end)

if not is_trading_time():
    print("当前非交易时间，实时数据可能不可用")
```

### 3. 量化框架集成问题

#### 问题：Backtrader适配器错误
```
AttributeError: 'BacktraderAdapter' object has no attribute 'get_data'
```

**解决方案：**
```python
# 正确使用Backtrader适配器
from src.quant_adapters import BacktraderAdapter

adapter = BacktraderAdapter()

# 获取数据用于Backtrader
data_feed = adapter.get_data_feed('000001', 
                                  start_date='2023-01-01',
                                  end_date='2023-12-31')

# 在Backtrader策略中使用
import backtrader as bt

class MyStrategy(bt.Strategy):
    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data, period=20)
    
    def next(self):
        if self.data.close[0] > self.sma[0]:
            self.buy()
```

#### 问题：VeighNa集成问题
```
ImportError: cannot import name 'VeighNaAdapter'
```

**解决方案：**
```python
# 确保正确导入和使用VeighNa适配器
from src.quant_adapters import VeighNaAdapter

# 创建适配器实例
adapter = VeighNaAdapter()

# 获取VeighNa格式的数据
bar_data = adapter.get_bar_data('000001.SZSE', 
                                start='2023-01-01',
                                end='2023-12-31')
```

### 4. 性能问题

#### 问题：数据获取速度慢
```
Warning: Data retrieval is taking longer than expected
```

**优化方案：**
```python
# 启用缓存
from src.unified_data_source import UnifiedDataSource

data_source = UnifiedDataSource()
data_source.enable_cache(cache_dir='./cache', expire_hours=1)

# 批量获取数据
symbols = ['000001', '000002', '600000']
data_dict = data_source.get_multiple_stocks(symbols, period='1d', count=100)
```

#### 问题：内存使用过高
```
MemoryError: Unable to allocate array
```

**解决方案：**
```python
# 分批处理大量数据
def process_large_dataset(symbols, batch_size=10):
    results = []
    for i in range(0, len(symbols), batch_size):
        batch = symbols[i:i+batch_size]
        batch_data = get_multiple_stocks(batch)
        results.extend(batch_data)
        # 清理内存
        import gc
        gc.collect()
    return results
```

### 5. Docker部署问题

#### 问题：Docker容器启动失败
```
Error: Container exited with code 1
```

**诊断步骤：**
```bash
# 查看容器日志
docker logs china-stock-data

# 进入容器调试
docker run -it --rm china-stock-data-source /bin/bash

# 检查健康状态
docker exec china-stock-data python health_check.py
```

**解决方案：**
```bash
# 重新构建镜像
docker build --no-cache -t china-stock-data-source .

# 使用docker-compose启动
docker-compose up --build

# 查看服务状态
docker-compose ps
```

#### 问题：端口访问问题
```
Error: Connection refused on port 8000
```

**解决方案：**
```bash
# 检查端口映射
docker ps

# 确保端口正确映射
docker run -p 8000:8000 -p 8888:8888 china-stock-data-source

# 测试端口连通性
curl http://localhost:8000/health
```

## 🔧 高级故障排除

### 启用调试模式
```python
# 在代码中启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 或设置环境变量
import os
os.environ['LOG_LEVEL'] = 'DEBUG'
```

### 网络诊断
```python
# 测试网络连接
import requests

def test_network_connectivity():
    test_urls = [
        'https://www.baidu.com',
        'https://xueqiu.com',
        'https://finance.sina.com.cn'
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=10)
            print(f"✓ {url}: {response.status_code}")
        except Exception as e:
            print(f"✗ {url}: {e}")
```

### 数据源状态检查
```python
# 检查各数据源状态
from src.unified_data_source import UnifiedDataSource

def check_data_sources():
    data_source = UnifiedDataSource()
    sources = ['akshare', 'tushare', 'yfinance']
    
    for source in sources:
        try:
            status = data_source.check_source_status(source)
            print(f"✓ {source}: {status}")
        except Exception as e:
            print(f"✗ {source}: {e}")
```

## 📞 获取帮助

### 自助诊断工具
```bash
# 运行完整诊断
python health_check.py --verbose

# 生成诊断报告
python health_check.py --report
```

### 社区支持
- **GitHub Issues**: [提交问题](https://github.com/minshengzhong3-byte/china-stock-data-source/issues)
- **讨论区**: [参与讨论](https://github.com/minshengzhong3-byte/china-stock-data-source/discussions)
- **Wiki**: [查看文档](https://github.com/minshengzhong3-byte/china-stock-data-source/wiki)

### 提交Bug报告

提交问题时，请包含以下信息：

1. **环境信息**：
   ```bash
   python --version
   pip list | grep -E "akshare|tushare|pandas|numpy"
   ```

2. **错误信息**：完整的错误堆栈跟踪

3. **重现步骤**：详细的操作步骤

4. **系统信息**：操作系统、Python版本等

5. **健康检查报告**：
   ```bash
   python health_check.py --report > health_report.txt
   ```

## 📚 相关文档

- [快速开始指南](README.md)
- [API参考文档](API_REFERENCE.md)
- [AI集成指南](AI_QUICK_START.md)
- [贡献指南](CONTRIBUTING.md)

---

**提示**: 如果问题仍未解决，请运行 `python health_check.py --report` 生成详细的诊断报告，并在GitHub Issues中提交。