# 东方财富研报下载工具

> 还在手动一个个下载研报？这个工具帮你一键搞定！

## 这是什么？

这是一个**命令行小工具**，可以帮你：
- 📋 查看有哪些行业研报
- 🔍 查询任何类型的研报（行业、策略、宏观、个股）
- 📥 一键下载研报PDF
- 📊 把研报信息导出成Excel表格

**一句话**：就像有个助手帮你从东方财富网站批量下载研报，你只需要下命令就行。

## 安装

### 快速安装

```bash
pip install eastmoney-reports
```

安装后可以使用以下命令：
- `eastmoney`（推荐）
- `report`（旧版）

### 从源码安装

```bash
# 从GitHub下载项目代码
git clone --depth 1 https://github.com/manymore13/eastmoney.git

# 进入项目文件夹
cd eastmoney

# 安装依赖
pip install -e .
```

### 安装依赖

```bash
pip install -r requirements.txt
```

### 完成！开始使用

---

## 新手入门（从零开始）

### 🥇 第一次使用：先看看有哪些行业

想知道东方财富有哪些行业分类？运行：

```bash
# 列出所有行业
eastmoney list
# 或者
report list
```

运行后你会看到一堆行业名称和代码，比如：
```
1001  农林牧渔
1002  化工
1003  钢铁
...
1046  游戏          <-- 这就是游戏行业的代码
```

### 🥈 想知道某个行业有什么研报？

比如我想看**游戏行业**的最新研报：

```bash
# 查询行业研报
eastmoney query -i 1046 -s 5
# -i 1046 = 游戏行业的代码是1046
# -s 5 = 只看最近5篇
```

看输出：
```
标题: 游戏行业周报：新品周期启动...
机构: 国信证券
日期: 2026-03-27
---
标题: 游戏行业深度报告：AI赋能...
机构: 中金公司
日期: 2026-03-26
...
```

### 🥉 想把研报信息保存到Excel？

查到了想要的研报，想保存下来？

```bash
# 查询结果保存为CSV文件（可以用Excel打开）
eastmoney query -i 1046 -s 10 --save-csv
```

运行后会在当前目录生成一个 `reports_行业_xxx.csv` 文件，用Excel打开就能看到表格。

---

## 进阶用法

### 场景1：我想看策略报告（市场分析）

策略报告是券商对市场行情的分析，比如"下周股市怎么走"这类。

```bash
# 查询策略报告
eastmoney query -t strategy -s 10
# -t strategy = 查策略报告
# -s 10 = 看最近10篇
```

### 场景2：我想看某只股票的研报

比如我想看**贵州茅台**的研报（股票代码600519）：

```bash
# 查询个股研报
eastmoney query -t stock -c 600519 -s 5
# -t stock = 查个股研报
# -c 600519 = 茅台的股票代码
```

### 场景3：我想下载几篇研报PDF

查到喜欢的研报后，下载保存到本地：

```bash
# 下载PDF
eastmoney download -t industry -i 1046 -s 3 -o ./reports
# -t industry = 下载行业研报
# -i 1046 = 游戏行业
# -s 3 = 下载最新的3篇
# -o ./reports = 保存到当前目录的reports文件夹
```

下载完成后，去 `reports/industry` 文件夹看看，PDF已经下好了！

### 场景4：下载策略报告PDF

```bash
# 下载最新的3篇策略报告
eastmoney download -t strategy -s 3 -o ./reports
```

### 场景5：批量下载所有行业的研报？

```bash
# 下载所有能找到的研报（注意：会下载很多！）
eastmoney download -t industry --all -o ./reports
```

---

## 命令大全

| 你想做什么 | 用的命令 | 例子 |
|------------|----------|------|
| 列出所有行业 | `eastmoney list` | `eastmoney list` |
| 搜索行业 | `eastmoney list -s 关键词` | `eastmoney list -s 游戏` |
| 查询研报 | `eastmoney query` | 见上面的例子 |
| 下载PDF | `eastmoney download` | 见上面的例子 |
| 导出Excel | `eastmoney query --save-csv` | `eastmoney query -i 1046 --save-csv` |

### 常用参数

| 参数 | 什么意思 | 怎么用 |
|------|----------|--------|
| `-t` | 研报类型 | `-t industry`（行业）、`-t strategy`（策略）、`-t stock`（个股） |
| `-i` | 行业代码 | `-i 1046`（游戏）、`-i 1001`（农业） |
| `-c` | 股票代码 | `-c 600519`（茅台）、`-c 000001`（平安） |
| `-s` | 要几条 | `-s 5`（5条）、`-s 20`（20条） |
| `-o` | 保存到哪 | `-o ./reports`（当前目录的reports文件夹） |
| `--save-csv` | 存为Excel | 加在query命令后面就行 |

### 研报类型对照表

| 类型 | 用途 | 例子 |
|------|------|------|
| `industry` | 行业分析报告 | 游戏、医疗、新能源 |
| `strategy` | 市场策略分析 | 大盘走势、操作建议 |
| `macro` | 宏观经济研究 | GDP、CPI、货币政策 |
| `morning` | 券商每天的晨报 | 每天早上的快讯 |
| `stock` | 单只股票分析 | 茅台、腾讯 |

---

## 常见问题

### Q: 运行提示"找不到report命令"？

Windows 用户确保用 `report.bat`：
```bash
report list
```

macOS/Linux 用户：
```bash
# 第一次需要加执行权限
chmod +x report

# 之后就可以用了
./report list
```

### Q: PDF下载失败？

确保电脑安装了curl（大多数电脑都有）：
```bash
# 检查是否已安装
curl --version
```

如果显示版本号就说明有了，否则需要安装。

### Q: 行业代码怎么查？

```bash
# 列出所有行业
eastmoney list

# 搜索包含"游戏"的行业
eastmoney list -s 游戏
```

### Q: 股票代码怎么查？

注意：接口不支持港股研报
直接用股票代码即可，比如：
- 茅台 = 600519
- 平安 = 000001

---

## 文件结构

```
eastmoney/
├── pyproject.toml      # 包配置文件
├── MANIFEST.in         # 包含数据文件
├── README.md           # 英文文档
├── README_zh.md        # 中文文档
├── LICENSE             # MIT许可证
├── src/
│   └── eastmoney/
│       ├── __init__.py     # 包初始化
│       ├── __main__.py     # 支持 python -m eastmoney
│       ├── cli.py          # 命令行接口
│       ├── report_client.py # 东方财富API客户端
│       ├── utils.py        # 工具函数
│       ├── mcp_server.py   # MCP服务器
│       └── data/
│           └── industry.json # 行业代码数据
├── .github/
│   └── workflows/
│       └── publish.yml     # PyPI发布工作流
└── tests/              # 测试目录
```

**通过 pip 安装后：**
```
# 可用的命令行工具：
eastmoney list
report list  # (旧版别名)
```

---

## 注意事项

1. **合理使用**：不要短时间内大量下载，给服务器留条活路 😂
2. **仅供学习**：下载的PDF仅供个人研究学习使用
3. **更新提醒**：如果东方财富 API 变了工具用不了，可以提 Issue

---

## MCP 协议支持

本包包含 MCP (Model Context Protocol) 服务器，允许 AI 智能体直接查询和下载研报。

### MCP 快速开始

安装后，MCP 服务器可作为命令行工具使用：

```bash
# 启动 MCP 服务器
eastmoney-mcp
```

### 通过提示词安装

对于支持提示词安装的 AI agent（如 Cursor、Cline），复制以下提示词：

```
请帮我安装和配置东方财富 MCP 服务器：

1. 安装包：pip install eastmoney-reports
2. 将以下配置添加到我的 MCP 配置文件（如 ~/.cursor/mcp.json 或 ~/.cline/mcp_config.json）：
{
  "mcpServers": {
    "eastmoney": {
      "command": "eastmoney-mcp",
      "description": "东方财富研报工具"
    }
  }
}
3. 验证安装：运行 eastmoney-mcp --version
```

### 一行安装（类似 npx）

使用 pipx（类似 Python 版的 npx）：

```bash
# 无需安装直接运行
pipx run eastmoney-reports eastmoney-mcp
```

如果还没安装 pipx：

```bash
pip install pipx
pipx ensurepath
```

### 在 AI 工具中配置

**Claude Desktop / Cursor / Cline：**

添加到 MCP 配置文件（如 `claude_desktop_config.json`）：

```json
{
  "mcpServers": {
    "eastmoney": {
      "command": "eastmoney-mcp",
      "description": "东方财富研报工具"
    }
  }
}
```

**可用的 MCP 工具：**
- `list_industries` - 列出所有行业
- `query_reports` - 查询研报
- `download_reports` - 下载研报 PDF
- `get_industry_code` - 按关键词搜索行业

---

## License

MIT License - 随便用，开心就好！

---

<div align="center">

**觉得好用？点个 ⭐ Star 支持一下！**

</div>
