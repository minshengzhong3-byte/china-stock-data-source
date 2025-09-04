# 贡献指南

感谢您对 China Stock Data Source 项目的关注！我们欢迎所有形式的贡献，包括但不限于：

- 🐛 Bug 报告
- 💡 功能建议
- 📝 文档改进
- 🔧 代码贡献
- 🧪 测试用例
- 📖 使用示例

## 🚀 快速开始

### 环境准备

1. **Fork 项目**
   ```bash
   # 在 GitHub 上 Fork 项目到您的账户
   # 然后克隆到本地
   git clone https://github.com/YOUR_USERNAME/china-stock-data-source.git
   cd china-stock-data-source
   ```

2. **设置开发环境**
   ```bash
   # 创建虚拟环境
   python -m venv venv
   
   # 激活虚拟环境
   # Windows:
   venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   
   # 安装依赖
   pip install -r requirements.txt
   pip install -e .
   ```

3. **安装开发工具**
   ```bash
   # 安装开发依赖
   pip install pytest pytest-cov flake8 black isort mypy
   ```

## 📋 贡献流程

### 1. 创建分支

```bash
# 创建并切换到新分支
git checkout -b feature/your-feature-name
# 或者
git checkout -b fix/your-bug-fix
```

分支命名规范：
- `feature/功能名称` - 新功能
- `fix/问题描述` - Bug修复
- `docs/文档类型` - 文档更新
- `test/测试内容` - 测试相关
- `refactor/重构内容` - 代码重构

### 2. 开发和测试

```bash
# 运行测试
python -m pytest tests/

# 运行代码质量检查
flake8 src/
black --check src/
isort --check-only src/
mypy src/

# 自动格式化代码
black src/
isort src/
```

### 3. 提交更改

```bash
# 添加更改
git add .

# 提交（请遵循提交信息规范）
git commit -m "feat: 添加新的数据源支持"

# 推送到您的 Fork
git push origin feature/your-feature-name
```

### 4. 创建 Pull Request

1. 在 GitHub 上打开您的 Fork
2. 点击 "New Pull Request"
3. 填写 PR 模板
4. 等待代码审查

## 📝 代码规范

### Python 代码风格

我们遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 代码风格指南：

```python
# ✅ 好的示例
def get_stock_data(symbol: str, start_date: str, end_date: str = None) -> Optional[pd.DataFrame]:
    """
    获取股票历史数据
    
    Args:
        symbol: 股票代码
        start_date: 开始日期
        end_date: 结束日期，默认为今天
    
    Returns:
        股票数据DataFrame，失败时返回None
    """
    pass

# ❌ 不好的示例
def getData(s,sd,ed=None):
    pass
```

### 工具配置

#### Black (代码格式化)
```bash
# 格式化所有代码
black src/ tests/ examples/

# 检查格式
black --check src/
```

#### isort (导入排序)
```bash
# 排序导入
isort src/ tests/ examples/

# 检查导入顺序
isort --check-only src/
```

#### flake8 (代码检查)
```bash
# 检查代码质量
flake8 src/ tests/
```

#### mypy (类型检查)
```bash
# 类型检查
mypy src/
```

### 提交信息规范

我们使用 [Conventional Commits](https://www.conventionalcommits.org/zh-hans/v1.0.0/) 规范：

```
<类型>[可选的作用域]: <描述>

[可选的正文]

[可选的脚注]
```

**类型说明：**
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

**示例：**
```
feat(data-source): 添加东方财富数据源支持

- 实现东方财富API接口
- 添加数据格式转换
- 更新数据源优先级配置

Closes #123
```

## 🧪 测试指南

### 测试类型

#### 1. 单元测试
```python
# tests/test_unified_data_source.py
import pytest
from unittest.mock import Mock, patch
from src.unified_data_source import UnifiedDataSource

def test_get_realtime_price_success():
    """测试成功获取实时价格"""
    ds = UnifiedDataSource()
    with patch.object(ds, '_fetch_from_source') as mock_fetch:
        mock_fetch.return_value = {'price': 10.5, 'change_percent': 2.3}
        result = ds.get_realtime_price('000001')
        assert result['price'] == 10.5
        assert result['change_percent'] == 2.3
```

#### 2. 集成测试
```python
def test_real_data_integration():
    """测试真实数据获取（需要网络）"""
    ds = UnifiedDataSource()
    result = ds.get_realtime_price('000001')
    # 注意：这个测试依赖网络，可能不稳定
    if result:  # 如果网络可用
        assert 'price' in result
        assert isinstance(result['price'], (int, float))
```

#### 3. 端到端测试
```python
def test_complete_workflow():
    """测试完整的工作流程"""
    ds = UnifiedDataSource()
    
    # 测试数据源状态
    status = ds.test_all_sources()
    assert isinstance(status, dict)
    
    # 测试实时数据
    price = ds.get_realtime_price('000001')
    # 根据网络情况判断
    
    # 测试历史数据
    history = ds.get_history_data('000001', '2024-01-01', '2024-01-31')
    # 根据网络情况判断
```

### 测试编写原则

1. **测试命名清晰**：`test_功能_场景_期望结果`
2. **独立性**：每个测试应该独立运行
3. **可重复**：测试结果应该一致
4. **快速执行**：避免长时间运行的测试
5. **有意义的断言**：验证关键行为和边界条件

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_unified_data_source.py

# 运行特定测试函数
pytest tests/test_unified_data_source.py::test_get_realtime_price

# 生成覆盖率报告
pytest --cov=src --cov-report=html

# 只运行快速测试（跳过网络测试）
pytest -m "not slow"
```

## 📖 文档贡献

### 文档类型

1. **API文档**：函数和类的docstring
2. **使用指南**：README.md 和示例代码
3. **开发文档**：CONTRIBUTING.md、CHANGELOG.md
4. **专题文档**：AI集成指南、最佳实践等

### 文档规范

#### Docstring 格式
```python
def get_stock_data(symbol: str, start_date: str, end_date: str = None) -> Optional[pd.DataFrame]:
    """
    获取股票历史数据
    
    这个函数从配置的数据源获取指定股票的历史K线数据，
    支持自动故障转移和数据质量验证。
    
    Args:
        symbol (str): 股票代码，支持6位数字格式（如'000001'）
        start_date (str): 开始日期，格式为'YYYY-MM-DD'
        end_date (str, optional): 结束日期，格式为'YYYY-MM-DD'。
                                 如果为None，则默认为当前日期。
    
    Returns:
        Optional[pd.DataFrame]: 包含以下列的DataFrame：
            - date: 日期
            - open: 开盘价
            - high: 最高价
            - low: 最低价
            - close: 收盘价
            - volume: 成交量
            如果获取失败，返回None。
    
    Raises:
        ValueError: 当股票代码格式不正确时
        ConnectionError: 当所有数据源都无法连接时
    
    Example:
        >>> ds = UnifiedDataSource()
        >>> data = ds.get_stock_data('000001', '2024-01-01', '2024-01-31')
        >>> if data is not None:
        ...     print(f"获取到 {len(data)} 条数据")
        获取到 21 条数据
    
    Note:
        - 数据源会按照优先级顺序尝试
        - 返回的数据已经过质量验证
        - 建议使用缓存以提高性能
    """
    pass
```

## 🐛 Bug 报告

### 报告模板

```markdown
## Bug 描述
简洁清晰地描述这个bug。

## 复现步骤
1. 执行 '...'
2. 点击 '....'
3. 滚动到 '....'
4. 看到错误

## 期望行为
清晰简洁地描述您期望发生什么。

## 实际行为
清晰简洁地描述实际发生了什么。

## 环境信息
- 操作系统: [例如 Windows 10, Ubuntu 20.04]
- Python 版本: [例如 3.9.7]
- 项目版本: [例如 1.0.0]
- 相关依赖版本: [例如 pandas 1.3.0]

## 错误日志
如果适用，请添加错误日志来帮助解释您的问题。

```python
# 粘贴相关代码
```

## 附加信息
添加任何其他有关问题的上下文信息。
```

## 💡 功能请求

### 请求模板

```markdown
## 功能描述
清晰简洁地描述您想要的功能。

## 问题背景
清晰简洁地描述这个功能要解决什么问题。例如：我总是很沮丧当[...]

## 解决方案
清晰简洁地描述您想要实现的解决方案。

## 替代方案
清晰简洁地描述您考虑过的任何替代解决方案或功能。

## 使用场景
描述这个功能的具体使用场景和用户故事。

## 附加信息
添加任何其他有关功能请求的上下文信息或截图。
```

## 🏆 贡献者认可

我们重视每一个贡献，所有贡献者都会在以下地方得到认可：

1. **README.md** - 贡献者列表
2. **CHANGELOG.md** - 版本更新记录
3. **GitHub Contributors** - 自动统计
4. **Release Notes** - 重要贡献特别感谢

## 📞 获取帮助

如果您在贡献过程中遇到任何问题，可以通过以下方式获取帮助：

- **GitHub Issues**: [提出问题](https://github.com/minshengzhong3-byte/china-stock-data-source/issues)
- **GitHub Discussions**: [参与讨论](https://github.com/minshengzhong3-byte/china-stock-data-source/discussions)
- **Email**: minshengzhong3@gmail.com

## 📜 行为准则

参与本项目即表示您同意遵守我们的行为准则：

### 我们的承诺

为了促进一个开放和友好的环境，我们作为贡献者和维护者承诺：无论年龄、体型、残疾、种族、性别认同和表达、经验水平、国籍、个人形象、种族、宗教或性取向如何，参与我们项目和社区的每个人都享有无骚扰的体验。

### 我们的标准

有助于创造积极环境的行为包括：

- 使用友好和包容的语言
- 尊重不同的观点和经验
- 优雅地接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表示同情

不可接受的行为包括：

- 使用性化的语言或图像以及不受欢迎的性关注或性骚扰
- 恶意评论、侮辱/贬损评论以及个人或政治攻击
- 公开或私下骚扰
- 未经明确许可发布他人的私人信息，如物理或电子地址
- 在专业环境中可能被合理认为不适当的其他行为

---

再次感谢您的贡献！🎉