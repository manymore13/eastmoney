FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制源码
COPY . .

# 暴露端口 (用于 HTTP transport)
EXPOSE 80

# 运行 MCP 服务器
CMD ["python", "-m", "mcp_server_fastmcp"]
