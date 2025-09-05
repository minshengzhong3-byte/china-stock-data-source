# 🤖 AI集成快速参考

> 5分钟快速上手指南

## ⚡ 极速开始

### 1. 安装
```bash
pip install pandas requests numpy
```

### 2. 基础用法
```python
from unified_data_source import get_stock_data, get_realtime_price

# 获取历史数据
data = get_stock_data('000001', period='1m')

# 获取实时价格
price = get_realtime_price('000001')
print(f"当前价格: {price['current_price']}")
```

## 📊 数据格式

### 历史数据
```python
# DataFrame格式
        date    open    high     low   close    volume
0  2024-01-01   12.20   12.45   12.15   12.30  8500000
1  2024-01-02   12.35   12.60   12.25   12.45  9200000
```

### 实时数据
```python
{
    'symbol': '000001',
    'current_price': 12.45,
    'change_percent': 1.88,
    'volume': 1000000,
    'timestamp': '2024-01-15 15:00:00'
}
```

## 🎯 AI应用场景

### 机器学习特征工程
```python
def create_ml_features(symbol):
    data = get_stock_data(symbol, period='6m')
    
    # 计算技术指标
    data['returns'] = data['close'].pct_change()
    data['ma5'] = data['close'].rolling(5).mean()
    data['volatility'] = data['returns'].rolling(20).std()
    
    return data[['returns', 'ma5', 'volatility']].dropna()
```

### 实时监控
```python
def monitor_stocks(symbols):
    results = []
    for symbol in symbols:
        price = get_realtime_price(symbol)
        results.append({
            'symbol': symbol,
            'price': price['current_price'],
            'change': price['change_percent']
        })
    return results
```

### 文本生成
```python
def generate_stock_summary(symbol):
    price = get_realtime_price(symbol)
    change = price['change_percent']
    
    trend = "上涨" if change > 0 else "下跌" if change < 0 else "平盘"
    return f"股票{symbol}当前价格{price['current_price']:.2f}元，{trend}{abs(change):.2f}%"
```

## 🛡️ 错误处理

```python
try:
    data = get_stock_data('000001')
except Exception as e:
    print(f"获取数据失败: {e}")
    # 使用备用方案或缓存数据
```

## ⚙️ 高级配置

```python
from unified_data_source import UnifiedDataSource

# 自定义配置
ds = UnifiedDataSource(
    source_priority=['ashare', 'abu'],  # 数据源优先级
    cache_enabled=True,                 # 启用缓存
    timeout=10                          # 超时时间
)

data = ds.get_history_data('000001')
```

## 📝 支持的参数

### period 参数
- `'1d'`, `'3d'`, `'1w'`, `'2w'`
- `'1m'`, `'3m'`, `'6m'`  
- `'1y'`, `'2y'`, `'5y'`

### 股票代码格式
- 标准格式: `'000001'`, `'600000'`
- 带前缀: `'SZ000001'`, `'SH600000'`

## 🔧 性能优化

1. **启用缓存**: 减少重复请求
2. **批量处理**: 一次处理多只股票
3. **合理超时**: 避免长时间等待
4. **异常处理**: 确保程序稳定运行

## 📞 获取帮助

- 📖 详细文档: `API_REFERENCE.md`
- 🔍 完整示例: `examples/ai_model_integration.py`
- 🚀 快速指南: `AI_QUICK_START.md`
- 🐛 问题反馈: GitHub Issues

---

**开始你的AI股票数据之旅！** 🚀