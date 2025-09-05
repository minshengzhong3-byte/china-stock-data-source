# 🤖 AI快速集成指南

> 专为大模型和AI应用设计的快速集成指南

## 🎯 核心概念

**China Stock Data Source** 是一个专为AI应用优化的A股数据获取模块，提供：

- **统一接口**：一套API获取多源数据
- **智能故障转移**：自动切换可用数据源
- **标准化格式**：AI友好的数据结构
- **高性能缓存**：减少重复请求
- **质量验证**：确保数据准确性

## ⚡ 30秒快速开始

### 1. 安装依赖
```bash
pip install pandas requests numpy
```

### 2. 基础使用
```python
from unified_data_source import get_stock_data, get_realtime_price

# 获取历史数据（AI训练用）
data = get_stock_data('000001', period='1y')
print(f"获取到 {len(data)} 条历史记录")

# 获取实时价格（AI推理用）
price = get_realtime_price('000001')
print(f"当前价格: {price['current_price']}")
```

### 3. 数据格式说明
```python
# 历史数据格式
{
    'date': '2024-01-15',
    'open': 10.50,
    'high': 10.80,
    'low': 10.30,
    'close': 10.65,
    'volume': 1000000,
    'amount': 10650000.0
}

# 实时数据格式
{
    'symbol': '000001',
    'current_price': 10.65,
    'change': 0.15,
    'change_percent': 1.43,
    'volume': 500000,
    'timestamp': '2024-01-15 15:00:00'
}
```

## 🎯 AI应用场景

### 场景1：股票价格监控
```python
def monitor_stocks(symbols):
    """监控多只股票价格变化"""
    results = []
    for symbol in symbols:
        try:
            price_data = get_realtime_price(symbol)
            results.append({
                'symbol': symbol,
                'price': price_data['current_price'],
                'change_percent': price_data['change_percent']
            })
        except Exception as e:
            print(f"获取 {symbol} 数据失败: {e}")
    return results

# 使用示例
watchlist = ['000001', '000002', '600000']
prices = monitor_stocks(watchlist)
```

### 场景2：技术分析数据准备
```python
def prepare_technical_data(symbol, period='6m'):
    """为技术分析准备数据"""
    data = get_stock_data(symbol, period=period)
    
    # 计算移动平均线
    data['ma5'] = data['close'].rolling(5).mean()
    data['ma20'] = data['close'].rolling(20).mean()
    
    # 计算RSI
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    data['rsi'] = 100 - (100 / (1 + rs))
    
    return data

# 使用示例
tech_data = prepare_technical_data('000001')
```

### 场景3：量化策略回测
```python
def simple_ma_strategy(symbol, short_window=5, long_window=20):
    """简单移动平均策略"""
    data = get_stock_data(symbol, period='1y')
    
    # 计算移动平均线
    data['ma_short'] = data['close'].rolling(short_window).mean()
    data['ma_long'] = data['close'].rolling(long_window).mean()
    
    # 生成交易信号
    data['signal'] = 0
    data.loc[data['ma_short'] > data['ma_long'], 'signal'] = 1
    data.loc[data['ma_short'] < data['ma_long'], 'signal'] = -1
    
    return data

# 使用示例
strategy_result = simple_ma_strategy('000001')
```

## 🔧 高级功能

### 自定义数据源优先级
```python
from unified_data_source import UnifiedDataSource

# 创建自定义配置的数据源
data_source = UnifiedDataSource(
    source_priority=['ashare', 'abu'],  # 优先使用ashare
    cache_enabled=True,
    timeout=10
)

# 使用自定义数据源
data = data_source.get_history_data('000001', period='3m')
```

### 批量数据获取
```python
def get_multiple_stocks(symbols, period='1m'):
    """批量获取多只股票数据"""
    results = {}
    for symbol in symbols:
        try:
            results[symbol] = get_stock_data(symbol, period=period)
            print(f"✓ {symbol} 数据获取成功")
        except Exception as e:
            print(f"✗ {symbol} 数据获取失败: {e}")
            results[symbol] = None
    return results

# 使用示例
stocks = ['000001', '000002', '600000', '600036']
all_data = get_multiple_stocks(stocks)
```

### 数据质量检查
```python
def validate_data_quality(data):
    """检查数据质量"""
    issues = []
    
    # 检查缺失值
    if data.isnull().any().any():
        issues.append("存在缺失值")
    
    # 检查异常价格
    if (data['high'] < data['low']).any():
        issues.append("存在异常价格数据")
    
    # 检查成交量
    if (data['volume'] < 0).any():
        issues.append("存在负成交量")
    
    return issues

# 使用示例
data = get_stock_data('000001')
issues = validate_data_quality(data)
if issues:
    print("数据质量问题:", issues)
else:
    print("数据质量良好")
```

## 🛡️ 错误处理最佳实践

### 基础错误处理
```python
def safe_get_stock_data(symbol, period='1m', max_retries=3):
    """安全的数据获取，带重试机制"""
    for attempt in range(max_retries):
        try:
            return get_stock_data(symbol, period=period)
        except Exception as e:
            print(f"第 {attempt + 1} 次尝试失败: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(1)  # 等待1秒后重试
```

### 重试机制
```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1):
    """重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

@retry_on_failure(max_retries=3, delay=2)
def robust_get_price(symbol):
    return get_realtime_price(symbol)
```

### 数据验证
```python
def validate_stock_data(data, symbol):
    """验证股票数据的完整性和合理性"""
    if data is None or len(data) == 0:
        raise ValueError(f"未获取到 {symbol} 的数据")
    
    required_columns = ['open', 'high', 'low', 'close', 'volume']
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        raise ValueError(f"缺少必要字段: {missing_columns}")
    
    # 检查价格合理性
    if (data['close'] <= 0).any():
        raise ValueError("存在非正价格数据")
    
    return True
```

## ⚡ 性能优化建议

### 1. 使用缓存
```python
# 启用缓存可显著提升重复查询性能
data_source = UnifiedDataSource(cache_enabled=True)
```

### 2. 批量处理
```python
# 批量获取比逐个获取更高效
symbols = ['000001', '000002', '600000']
results = {symbol: get_stock_data(symbol) for symbol in symbols}
```

### 3. 异步处理
```python
import asyncio
import concurrent.futures

def get_data_async(symbols):
    """异步获取多只股票数据"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(get_stock_data, symbol): symbol for symbol in symbols}
        results = {}
        for future in concurrent.futures.as_completed(futures):
            symbol = futures[future]
            try:
                results[symbol] = future.result()
            except Exception as e:
                print(f"获取 {symbol} 数据失败: {e}")
        return results
```

## ✅ AI集成检查清单

在将模块集成到AI应用前，请确认：

- [ ] **依赖安装**：pandas, requests, numpy已安装
- [ ] **网络连接**：确保能访问数据源API
- [ ] **数据格式**：了解返回的数据结构
- [ ] **错误处理**：实现了适当的异常处理
- [ ] **性能考虑**：根据需要启用缓存和批量处理
- [ ] **数据验证**：添加了数据质量检查
- [ ] **监控日志**：实现了适当的日志记录

## 🤔 常见问题

**Q: 如何处理数据源不可用的情况？**
A: 模块内置智能故障转移，会自动尝试其他数据源。你也可以通过 `source_priority` 参数自定义优先级。

**Q: 数据更新频率如何？**
A: 实时数据通常有15分钟延迟，历史数据每日更新。具体频率取决于数据源。

**Q: 如何提高数据获取速度？**
A: 启用缓存、使用批量获取、合理设置超时时间，避免频繁的小批量请求。

**Q: 支持哪些股票代码格式？**
A: 支持标准6位代码（如000001）和带前缀格式（如SZ000001），模块会自动标准化。

## 📞 获取帮助

- **文档**：查看 `API_REFERENCE.md` 获取详细API说明
- **示例**：参考 `examples/` 目录中的完整示例
- **问题反馈**：通过GitHub Issues报告问题
- **社区讨论**：加入我们的开发者社区

---

🎉 **开始你的AI股票数据之旅吧！**