# 📚 API参考文档

> China Stock Data Source 模块完整API参考

## 🚀 快速开始

```python
from unified_data_source import UnifiedDataSource, get_stock_data, get_realtime_price

# 方式1：使用便捷函数
data = get_stock_data('000001', period='1m')
price = get_realtime_price('000001')

# 方式2：使用类实例
ds = UnifiedDataSource()
data = ds.get_history_data('000001', period='1m')
price = ds.get_realtime_price('000001')
```

## 🏗️ 核心类

### UnifiedDataSource

统一数据源类，提供股票数据获取的核心功能。

#### 构造函数

```python
UnifiedDataSource(
    source_priority=['ashare', 'abu'],
    cache_enabled=True,
    cache_duration=300,
    timeout=10,
    max_retries=3
)
```

**参数说明：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `source_priority` | List[str] | `['ashare', 'abu']` | 数据源优先级列表 |
| `cache_enabled` | bool | `True` | 是否启用缓存 |
| `cache_duration` | int | `300` | 缓存持续时间（秒） |
| `timeout` | int | `10` | 请求超时时间（秒） |
| `max_retries` | int | `3` | 最大重试次数 |

#### 方法

##### get_realtime_price(symbol)

获取股票实时价格信息。

```python
price_data = ds.get_realtime_price('000001')
```

**参数：**
- `symbol` (str): 股票代码，支持6位数字格式

**返回值：**
```python
{
    'symbol': '000001',           # 股票代码
    'current_price': 10.65,       # 当前价格
    'change': 0.15,               # 涨跌额
    'change_percent': 1.43,       # 涨跌幅(%)
    'volume': 500000,             # 成交量
    'amount': 5325000.0,          # 成交额
    'high': 10.80,                # 最高价
    'low': 10.30,                 # 最低价
    'open': 10.50,                # 开盘价
    'pre_close': 10.50,           # 昨收价
    'timestamp': '2024-01-15 15:00:00'  # 数据时间戳
}
```

**异常：**
- `ValueError`: 股票代码格式错误
- `ConnectionError`: 网络连接失败
- `DataSourceError`: 所有数据源都不可用

##### get_history_data(symbol, period='1m', start_date=None, end_date=None)

获取股票历史数据。

```python
history_data = ds.get_history_data('000001', period='6m')
```

**参数：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `symbol` | str | - | 股票代码 |
| `period` | str | `'1m'` | 时间周期 |
| `start_date` | str | None | 开始日期 (YYYY-MM-DD) |
| `end_date` | str | None | 结束日期 (YYYY-MM-DD) |

**period 支持的值：**
- `'1d'`, `'3d'`, `'1w'`, `'2w'`, `'1m'`, `'3m'`, `'6m'`, `'1y'`, `'2y'`, `'5y'`

**返回值：**
Pandas DataFrame，包含以下列：

| 列名 | 类型 | 说明 |
|------|------|------|
| `date` | str | 交易日期 |
| `open` | float | 开盘价 |
| `high` | float | 最高价 |
| `low` | float | 最低价 |
| `close` | float | 收盘价 |
| `volume` | int | 成交量 |
| `amount` | float | 成交额 |

##### normalize_symbol(symbol)

标准化股票代码格式。

```python
std_symbol = ds.normalize_symbol('SZ000001')  # 返回 '000001'
```

**参数：**
- `symbol` (str): 原始股票代码

**返回值：**
- `str`: 标准化后的6位股票代码

##### test_all_sources()

测试所有数据源的可用性。

```python
status = ds.test_all_sources()
```

**返回值：**
```python
{
    'ashare': {
        'available': True,
        'response_time': 0.5,
        'error': None
    },
    'abu': {
        'available': False,
        'response_time': None,
        'error': 'Connection timeout'
    }
}
```

##### get_usage_stats()

获取使用统计信息。

```python
stats = ds.get_usage_stats()
```

**返回值：**
```python
{
    'total_requests': 150,
    'successful_requests': 145,
    'failed_requests': 5,
    'cache_hits': 80,
    'cache_misses': 70,
    'average_response_time': 0.8,
    'source_usage': {
        'ashare': 120,
        'abu': 25
    }
}
```

## 🔧 主要函数

### get_stock_data(symbol, period='1m', **kwargs)

便捷函数，获取股票历史数据。

```python
from unified_data_source import get_stock_data

data = get_stock_data('000001', period='3m')
```

**参数：**
- 与 `UnifiedDataSource.get_history_data()` 相同

**返回值：**
- 与 `UnifiedDataSource.get_history_data()` 相同

### get_realtime_price(symbol, **kwargs)

便捷函数，获取股票实时价格。

```python
from unified_data_source import get_realtime_price

price = get_realtime_price('000001')
```

**参数：**
- 与 `UnifiedDataSource.get_realtime_price()` 相同

**返回值：**
- 与 `UnifiedDataSource.get_realtime_price()` 相同

## 📊 数据格式

### 实时数据格式

```python
{
    "symbol": "000001",              # 股票代码
    "name": "平安银行",               # 股票名称
    "current_price": 12.45,          # 当前价格
    "change": 0.23,                  # 涨跌额
    "change_percent": 1.88,          # 涨跌幅(%)
    "volume": 15420000,              # 成交量(股)
    "amount": 191532000.0,           # 成交额(元)
    "turnover_rate": 0.85,           # 换手率(%)
    "pe_ratio": 5.2,                 # 市盈率
    "pb_ratio": 0.6,                 # 市净率
    "high": 12.58,                   # 今日最高价
    "low": 12.20,                    # 今日最低价
    "open": 12.30,                   # 今日开盘价
    "pre_close": 12.22,              # 昨日收盘价
    "market_cap": 241500000000.0,    # 总市值(元)
    "circulation_cap": 193200000000.0, # 流通市值(元)
    "timestamp": "2024-01-15 15:00:00", # 数据时间戳
    "source": "ashare"               # 数据来源
}
```

### 历史数据格式

```python
# DataFrame 格式
        date    open    high     low   close    volume        amount
0  2024-01-01   12.20   12.45   12.15   12.30  8500000   104550000.0
1  2024-01-02   12.35   12.60   12.25   12.45  9200000   114540000.0
2  2024-01-03   12.40   12.55   12.30   12.50  7800000    97110000.0
...
```

**字段说明：**

| 字段 | 类型 | 说明 | 单位 |
|------|------|------|------|
| `date` | str | 交易日期 | YYYY-MM-DD |
| `open` | float | 开盘价 | 元 |
| `high` | float | 最高价 | 元 |
| `low` | float | 最低价 | 元 |
| `close` | float | 收盘价 | 元 |
| `volume` | int | 成交量 | 股 |
| `amount` | float | 成交额 | 元 |

## ⚠️ 错误处理

### 异常类型

```python
# 自定义异常
class DataSourceError(Exception):
    """数据源错误"""
    pass

class ValidationError(Exception):
    """数据验证错误"""
    pass

class NetworkError(Exception):
    """网络连接错误"""
    pass
```

### 错误处理示例

```python
try:
    data = get_stock_data('000001')
except DataSourceError as e:
    print(f"数据源错误: {e}")
    # 尝试其他方案或使用缓存数据
except ValidationError as e:
    print(f"数据验证失败: {e}")
    # 检查输入参数
except NetworkError as e:
    print(f"网络连接失败: {e}")
    # 检查网络连接或稍后重试
except Exception as e:
    print(f"未知错误: {e}")
    # 记录日志并处理
```

## ⚙️ 配置选项

### 环境变量

```bash
# 设置默认数据源优先级
export STOCK_DATA_SOURCES="ashare,abu"

# 设置缓存配置
export STOCK_DATA_CACHE_ENABLED="true"
export STOCK_DATA_CACHE_DURATION="300"

# 设置网络配置
export STOCK_DATA_TIMEOUT="10"
export STOCK_DATA_MAX_RETRIES="3"
```

### 配置文件

创建 `config.json`：

```json
{
    "data_sources": {
        "priority": ["ashare", "abu"],
        "timeout": 10,
        "max_retries": 3
    },
    "cache": {
        "enabled": true,
        "duration": 300,
        "max_size": 1000
    },
    "logging": {
        "level": "INFO",
        "file": "stock_data.log"
    }
}
```

## 📝 使用示例

### 基础使用

```python
from unified_data_source import UnifiedDataSource

# 创建数据源实例
ds = UnifiedDataSource()

# 获取实时价格
price = ds.get_realtime_price('000001')
print(f"平安银行当前价格: {price['current_price']}")

# 获取历史数据
data = ds.get_history_data('000001', period='1m')
print(f"获取到 {len(data)} 条历史记录")
```

### 批量获取

```python
symbols = ['000001', '000002', '600000', '600036']
results = {}

for symbol in symbols:
    try:
        results[symbol] = ds.get_realtime_price(symbol)
        print(f"✓ {symbol}: {results[symbol]['current_price']}")
    except Exception as e:
        print(f"✗ {symbol}: {e}")
```

### 数据质量检查

```python
def check_data_quality(data):
    """检查数据质量"""
    issues = []
    
    # 检查必要字段
    required_fields = ['open', 'high', 'low', 'close', 'volume']
    missing_fields = [f for f in required_fields if f not in data.columns]
    if missing_fields:
        issues.append(f"缺少字段: {missing_fields}")
    
    # 检查数据完整性
    if data.isnull().any().any():
        issues.append("存在空值")
    
    # 检查价格合理性
    if (data['high'] < data['low']).any():
        issues.append("最高价低于最低价")
    
    if (data['close'] <= 0).any():
        issues.append("存在非正价格")
    
    return issues

# 使用示例
data = get_stock_data('000001')
issues = check_data_quality(data)
if issues:
    print("数据质量问题:", issues)
else:
    print("数据质量良好")
```

### 性能监控

```python
import time

def monitor_performance():
    """监控数据获取性能"""
    ds = UnifiedDataSource()
    
    # 测试实时数据获取
    start_time = time.time()
    try:
        price = ds.get_realtime_price('000001')
        realtime_duration = time.time() - start_time
        print(f"实时数据获取耗时: {realtime_duration:.2f}秒")
    except Exception as e:
        print(f"实时数据获取失败: {e}")
    
    # 测试历史数据获取
    start_time = time.time()
    try:
        data = ds.get_history_data('000001', period='1m')
        history_duration = time.time() - start_time
        print(f"历史数据获取耗时: {history_duration:.2f}秒")
        print(f"获取记录数: {len(data)}")
    except Exception as e:
        print(f"历史数据获取失败: {e}")
    
    # 获取使用统计
    stats = ds.get_usage_stats()
    print(f"缓存命中率: {stats['cache_hits'] / (stats['cache_hits'] + stats['cache_misses']) * 100:.1f}%")

# 运行监控
monitor_performance()
```

### AI模型集成

```python
import pandas as pd
from sklearn.preprocessing import StandardScaler

def prepare_ml_features(symbol, period='6m'):
    """为机器学习准备特征数据"""
    # 获取历史数据
    data = get_stock_data(symbol, period=period)
    
    # 计算技术指标
    data['returns'] = data['close'].pct_change()
    data['ma5'] = data['close'].rolling(5).mean()
    data['ma20'] = data['close'].rolling(20).mean()
    data['volatility'] = data['returns'].rolling(20).std()
    
    # 计算RSI
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    data['rsi'] = 100 - (100 / (1 + rs))
    
    # 选择特征列
    feature_columns = ['returns', 'ma5', 'ma20', 'volatility', 'rsi', 'volume']
    features = data[feature_columns].dropna()
    
    # 标准化
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    return pd.DataFrame(features_scaled, columns=feature_columns, index=features.index)

# 使用示例
features = prepare_ml_features('000001')
print(f"特征数据形状: {features.shape}")
print(features.head())
```

## 🔍 调试和监控

### 启用详细日志

```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_data.log'),
        logging.StreamHandler()
    ]
)

# 创建数据源实例（会自动记录详细日志）
ds = UnifiedDataSource()
```

### 性能分析

```python
import cProfile
import pstats

def profile_data_fetching():
    """分析数据获取性能"""
    pr = cProfile.Profile()
    pr.enable()
    
    # 执行数据获取操作
    ds = UnifiedDataSource()
    for i in range(10):
        data = ds.get_realtime_price('000001')
    
    pr.disable()
    
    # 输出性能报告
    stats = pstats.Stats(pr)
    stats.sort_stats('cumulative')
    stats.print_stats(10)

# 运行性能分析
profile_data_fetching()
```

---

## 📞 技术支持

如果您在使用过程中遇到问题，请：

1. 查看本文档的相关章节
2. 检查 [常见问题](README.md#常见问题)
3. 提交 [GitHub Issue](https://github.com/minshengzhong3-byte/china-stock-data-source/issues)
4. 参与社区讨论

---

*最后更新: 2024-01-15*