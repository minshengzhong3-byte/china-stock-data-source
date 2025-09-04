# 🚀 China Stock Data Source

一个专为中国A股市场设计的统一数据源模块，整合多个数据提供商，提供稳定可靠的股票数据获取服务。

## ✨ 核心特性

### 🔄 多数据源支持
- **ABu量化框架集成** - 基于成熟的量化交易框架
- **AShare数据源** - 高质量的A股数据接口
- **智能故障转移** - 自动切换可用数据源
- **负载均衡** - 分散请求压力，提高稳定性

### 🛡️ 统一数据格式
- **标准化接口** - 统一的数据结构和调用方式
- **数据质量验证** - 自动检测和过滤异常数据
- **格式转换** - 自动处理不同数据源的格式差异
- **类型安全** - 完整的类型注解和验证

### ⚡ 高性能缓存
- **智能缓存策略** - 减少重复请求，提高响应速度
- **可配置过期时间** - 灵活的缓存管理
- **内存优化** - 高效的内存使用和垃圾回收
- **并发安全** - 支持多线程环境

### 🤖 AI友好设计
- **简洁API** - 专为大模型设计的直观接口
- **丰富示例** - 完整的AI集成示例和文档
- **特征工程** - 内置常用技术指标计算
- **批量处理** - 支持高效的批量数据获取

### 📊 量化交易优化
- **实时数据** - 毫秒级的实时价格更新
- **历史数据** - 完整的历史K线数据
- **技术指标** - 内置常用技术分析指标
- **回测支持** - 为策略回测优化的数据格式

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 基本使用

```python
from unified_data_source import UnifiedDataSource, get_realtime_price

# 创建数据源实例
ds = UnifiedDataSource()

# 获取实时股票价格
price_info = ds.get_realtime_price('000001')
print(f"平安银行当前价格: {price_info['price']}")

# 获取历史数据
history_data = ds.get_history_data(
    symbol='000001',
    start_date='2024-01-01',
    end_date='2024-01-31'
)
print(f"获取到 {len(history_data)} 条历史数据")
```

## 📁 项目结构

```
china-stock-data-source/
├── src/                          # 核心源代码
│   ├── __init__.py              # 包初始化
│   ├── unified_data_source.py   # 统一数据源主模块
│   ├── abu_source.py            # ABu数据源适配器
│   └── ashare_source.py         # AShare数据源适配器
├── examples/                     # 使用示例
│   ├── quantitative_trading_example.py  # 量化交易示例
│   ├── ai_integration_guide.py          # AI集成指南
│   └── ai_model_integration.py          # AI模型集成示例
├── tests/                       # 测试文件
│   └── test_unified_data_source.py     # 单元测试
├── docs/                        # 文档
│   ├── AI_QUICK_START.md        # AI快速开始指南
│   ├── AI_INTEGRATION_QUICK_REFERENCE.md # AI集成快速参考
│   └── API_REFERENCE.md         # API参考文档
├── .github/workflows/           # CI/CD配置
│   └── ci.yml                   # GitHub Actions工作流
├── requirements.txt             # 项目依赖
├── pyproject.toml              # 项目配置
├── setup.py                    # 安装脚本
├── Dockerfile                  # Docker配置
├── .gitignore                  # Git忽略文件
├── CHANGELOG.md                # 更新日志
├── CONTRIBUTING.md             # 贡献指南
└── README.md                   # 项目说明
```

## 🔧 数据源优先级

系统按以下优先级尝试数据源：

1. **ABu数据源** - 主要数据源，稳定性高
2. **AShare数据源** - 备用数据源，数据丰富
3. **自动故障转移** - 智能切换到可用源

可以通过配置自定义优先级：

```python
ds = UnifiedDataSource(source_priority=['ashare', 'abu'])
```

## 🤖 AI集成指南

### 为大模型开发者

本模块专为AI应用设计，提供简洁直观的接口：

```python
# 快速获取股票特征数据
from examples.ai_model_integration import AIStockDataProvider

ai_provider = AIStockDataProvider()
features = ai_provider.get_stock_features('000001', days=60)

# 特征数据包含：
# - 技术指标 (RSI, MACD, 移动平均等)
# - 价格变化 (1日、5日、20日收益率)
# - 成交量指标 (成交量比率、平均成交量)
# - 波动率和风险指标
```

### 量化策略集成

```python
# 简单移动平均策略示例
def simple_ma_strategy(symbol, short_window=5, long_window=20):
    # 获取历史数据
    df = ds.get_history_data(symbol, start_date='2024-01-01')
    
    # 计算移动平均
    df['ma_short'] = df['close'].rolling(short_window).mean()
    df['ma_long'] = df['close'].rolling(long_window).mean()
    
    # 生成交易信号
    df['signal'] = 0
    df.loc[df['ma_short'] > df['ma_long'], 'signal'] = 1  # 买入信号
    df.loc[df['ma_short'] < df['ma_long'], 'signal'] = -1  # 卖出信号
    
    return df

# 使用示例
strategy_result = simple_ma_strategy('000001')
print(f"最新信号: {strategy_result['signal'].iloc[-1]}")
```

## 📊 量化交易示例

完整的量化交易示例请参考 `examples/quantitative_trading_example.py`：

```python
from unified_data_source import get_stock_data, get_realtime_price

# 获取股票数据
stock_data = get_stock_data('000001', days=30)
if stock_data is not None:
    print(f"获取到 {len(stock_data)} 条数据")
    
    # 计算简单移动平均
    stock_data['MA5'] = stock_data['close'].rolling(5).mean()
    stock_data['MA20'] = stock_data['close'].rolling(20).mean()
    
    # 获取最新价格
    current_price = get_realtime_price('000001')
    if current_price:
        print(f"当前价格: {current_price['price']}")
        print(f"涨跌幅: {current_price['change_percent']:.2f}%")
else:
    print("无法获取股票数据")
```

## 📚 API参考

### 主要函数

#### `get_stock_data(symbol, start_date, end_date, **kwargs)`

获取股票历史数据。

**参数：**
- `symbol` (str): 股票代码，如 '000001'
- `start_date` (str): 开始日期，格式 'YYYY-MM-DD'
- `end_date` (str, 可选): 结束日期，默认为今天
- `**kwargs`: 其他参数

**返回：**
- `pandas.DataFrame`: 包含开高低收量等数据的DataFrame
- `None`: 获取失败时返回

#### `get_realtime_price(symbol, **kwargs)`

获取股票实时价格信息。

**参数：**
- `symbol` (str): 股票代码
- `**kwargs`: 其他参数

**返回：**
- `dict`: 包含价格、涨跌幅、成交量等信息的字典
- `None`: 获取失败时返回

### UnifiedDataSource类

#### 初始化参数

```python
UnifiedDataSource(
    source_priority=['abu', 'ashare'],  # 数据源优先级
    cache_expire=300,                   # 缓存过期时间(秒)
    max_retries=3,                      # 最大重试次数
    timeout=10                          # 请求超时时间(秒)
)
```

#### 核心方法

- `get_realtime_price(symbol)` - 获取实时价格
- `get_history_data(symbol, start_date, end_date)` - 获取历史数据
- `normalize_symbol(symbol)` - 标准化股票代码
- `test_all_sources()` - 测试所有数据源状态
- `get_usage_stats()` - 获取使用统计信息

## 🛠️ 开发指南

### 本地开发

1. 克隆仓库：
```bash
git clone https://github.com/minshengzhong3-byte/china-stock-data-source.git
cd china-stock-data-source
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行测试：
```bash
python -m pytest tests/
```

### 添加新数据源

1. 在 `src/` 目录下创建新的数据源适配器
2. 实现标准接口：`get_realtime_price()` 和 `get_history_data()`
3. 在 `unified_data_source.py` 中注册新数据源
4. 添加相应的测试用例

## 🤝 贡献指南

我们欢迎所有形式的贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细信息。

### 代码规范

- 遵循 PEP 8 代码风格
- 使用 Black 进行代码格式化
- 添加类型注解
- 编写单元测试
- 更新相关文档

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [ABu量化交易系统](https://github.com/bbfamily/abu) - 提供核心量化框架支持
- [AShare](https://github.com/jindaxiang/akshare) - 提供丰富的A股数据接口
- 所有贡献者和用户的支持

## 📞 联系我们

- **GitHub Issues**: [提交问题和建议](https://github.com/minshengzhong3-byte/china-stock-data-source/issues)
- **Email**: minshengzhong3@gmail.com
- **项目主页**: https://github.com/minshengzhong3-byte/china-stock-data-source

## 📈 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本更新历史。

---

⭐ 如果这个项目对你有帮助，请给我们一个星标！

🔄 持续更新中，欢迎关注项目动态！