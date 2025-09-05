# China Stock Data Source - 生产级Docker镜像
# 提供开箱即用的股票数据服务

FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Shanghai

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    wget \
    vim \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# 设置时区
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 安装额外的量化和数据分析库
RUN pip install --no-cache-dir \
    akshare>=1.8.0 \
    tushare>=1.2.0 \
    yfinance>=0.1.70 \
    matplotlib>=3.3.0 \
    seaborn>=0.11.0 \
    jupyter>=1.0.0 \
    jupyterlab>=3.0.0 \
    -i https://mirrors.aliyun.com/pypi/simple/

# 复制项目文件
COPY src/ ./src/
COPY examples/ ./examples/
COPY *.py ./
COPY *.md ./

# 创建数据和日志目录
RUN mkdir -p /app/data /app/logs /app/cache

# 设置权限
RUN chmod +x *.py

# 运行健康检查
RUN python health_check.py --check-only || echo "健康检查完成"

# 暴露端口（用于Jupyter和API服务）
EXPOSE 8888 8000

# 创建启动脚本
RUN echo '#!/bin/bash\n\
echo "🚀 启动 China Stock Data Source 服务..."\n\
echo "==========================================="\n\
\n\
# 运行健康检查\n\
echo "🔍 运行健康检查..."\n\
python health_check.py\n\
\n\
if [ $? -eq 0 ]; then\n\
    echo "✅ 健康检查通过"\n\
else\n\
    echo "⚠️ 健康检查发现问题，但继续启动服务"\n\
fi\n\
\n\
echo "\n📊 启动数据服务..."\n\
\n\
# 根据参数决定启动模式\n\
if [ "$1" = "jupyter" ]; then\n\
    echo "🔬 启动Jupyter Lab..."\n\
    jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token="" --NotebookApp.password=""\n\
elif [ "$1" = "api" ]; then\n\
    echo "🌐 启动API服务..."\n\
    python -c "\n\
from flask import Flask, jsonify, request\n\
from src.unified_data_source import get_stock_data, get_realtime_price\n\
from src.quant_adapters import UniversalAdapter\n\
import traceback\n\
\n\
app = Flask(__name__)\n\
adapter = UniversalAdapter()\n\
\n\
@app.route('/health')\n\
def health_check():\n\
    return jsonify({'status': 'ok', 'service': 'China Stock Data Source'})\n\
\n\
@app.route('/stock/<symbol>/realtime')\n\
def get_realtime(symbol):\n\
    try:\n\
        data = get_realtime_price(symbol)\n\
        return jsonify({'success': True, 'data': data})\n\
    except Exception as e:\n\
        return jsonify({'success': False, 'error': str(e)}), 500\n\
\n\
@app.route('/stock/<symbol>/history')\n\
def get_history(symbol):\n\
    try:\n\
        period = request.args.get('period', '1d')\n\
        count = int(request.args.get('count', 100))\n\
        data = get_stock_data(symbol, period=period, count=count)\n\
        if data is not None:\n\
            return jsonify({'success': True, 'data': data.to_dict('records')})\n\
        else:\n\
            return jsonify({'success': False, 'error': 'No data found'}), 404\n\
    except Exception as e:\n\
        return jsonify({'success': False, 'error': str(e)}), 500\n\
\n\
if __name__ == '__\'__main__\':\n\
    app.run(host='0.0.0.0', port=8000, debug=True)\n\
"\n\
else\n\
    echo "🎯 启动交互式Python环境..."\n\
    echo "可用的模块:"\n\
    echo "  - from src.unified_data_source import get_stock_data, get_realtime_price"\n\
    echo "  - from src.quant_adapters import UniversalAdapter"\n\
    echo ""\n\
    echo "快速测试:"\n\
    echo "  python quick_start.py"\n\
    echo ""\n\
    python\n\
fi\n\
' > /app/start.sh && chmod +x /app/start.sh

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from src.unified_data_source import get_realtime_price; print('OK' if get_realtime_price('000001') else 'FAIL')"

# 默认启动命令
CMD ["/app/start.sh"]