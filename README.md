# Eastmoney Research Reports Tool

> 还在手动一个个下载研报？这个工具帮你一键搞定！  
> Tired of downloading reports one by one? This tool does it all with one command!

## What is this? | 这是什么？

A **command-line tool** that helps you:
- 📋 List all industry research reports
- 🔍 Query any type of report (industry, strategy, macro, stock)
- 📥 Download research report PDFs in batch
- 📊 Export report info to Excel/CSV

**In short**: It's like having an assistant to batch download reports from Eastmoney website.

这是一个**命令行小工具**，可以帮你：
- 📋 查看有哪些行业研报
- 🔍 查询任何类型的研报（行业、策略、宏观、个股）
- 📥 一键下载研报PDF
- 📊 把研报信息导出成Excel表格

**一句话**：就像有个助手帮你从东方财富网站批量下载研报，你只需要下命令就行。

## Installation | 安装

### Quick Install | 快速安装

```bash
pip install eastmoney-reports
```

After installation, you can use either command:
- `eastmoney` (recommended)
- `report` (legacy)

安装后可以使用以下命令：
- `eastmoney`（推荐）
- `report`（旧版）

### Alternative: Install from Source | 或者：从源码安装

### 第1步：下载项目

打开终端（Windows上叫"命令提示符"或"PowerShell"），输入：

```bash
# 从GitHub下载项目代码
git clone --depth 1 https://github.com/manymore13/eastmoney.git

# 进入项目文件夹
cd eastmoney

# 安装依赖
pip install -e .
```

### Step 2: Install Dependencies | 安装依赖

```bash
pip install -r requirements.txt
```

### Step 3: Ready to Use! | 完成！开始使用

---

## 新手入门（从零开始）| Getting Started

### 🥇 First Time: List All Industries | 第一次使用：先看看有哪些行业

想知道东方财富有哪些行业分类？运行：

```bash
# List all industries | 列出所有行业
eastmoney list
# or | 或者
report list
```

### 🥈 Query Industry Reports | 想知道某个行业有什么研报？

比如我想看**游戏行业**的最新研报：

```bash
# Query industry reports | 查询行业研报
eastmoney query -i 1046 -s 5
# -i 1046 = industry code for gaming | 行业代码（游戏行业是1046）
# -s 5 = show 5 latest reports | 只看最近5篇
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

### 🥉 Save to CSV/Excel | 想把研报信息保存到Excel？

查到了想要的研报，想保存下来？

```bash
# Save results as CSV | 查询结果保存为CSV文件（可以用Excel打开）
eastmoney query -i 1046 -s 10 --save-csv
```

运行后会在当前目录生成一个 `reports_行业_xxx.csv` 文件，用Excel打开就能看到表格。

---

## 进阶用法 | Advanced Usage

### Scenario 1: Strategy Reports | 场景1：我想看策略报告（市场分析）

策略报告是券商对市场行情的分析，比如"下周股市怎么走"这类。

```bash
# Query strategy reports | 查询策略报告
eastmoney query -t strategy -s 10
# -t strategy = strategy reports | 查策略报告
# -s 10 = show 10 latest | 看最近10篇
```

### Scenario 2: Stock Reports | 场景2：我想看某只股票的研报

比如我想看**贵州茅台**的研报（股票代码600519）：

```bash
# Query stock reports | 查询个股研报
eastmoney query -t stock -c 600519 -s 5
# -t stock = stock report | 查个股研报
# -c 600519 = stock code for Moutai | 茅台的股票代码
```

### Scenario 3: Download PDF Reports | 场景3：我想下载几篇研报PDF

查到喜欢的研报后，下载保存到本地：

```bash
# Download PDF | 下载PDF
eastmoney download -t industry -i 1046 -s 3 -o ./reports
# -t industry = industry report | 下载行业研报
# -i 1046 = gaming industry | 游戏行业
# -s 3 = download 3 latest | 下载最新的3篇
# -o ./reports = save to reports folder | 保存到当前目录的reports文件夹
```

下载完成后，去 `reports/industry` 文件夹看看，PDF已经下好了！

### Scenario 4: Download Strategy Reports PDF | 场景4：下载策略报告PDF

```bash
# Download latest 3 strategy reports | 下载最新的3篇策略报告
eastmoney download -t strategy -s 3 -o ./reports
```

### Scenario 5: Batch Download All Industries | 场景5：批量下载所有行业的研报？

```bash
# Download all available reports (warning: lots of downloads!) | 下载所有能找到的研报（注意：会下载很多！）
eastmoney download -t industry --all -o ./reports
```

---

## 命令大全 | Command Reference

| What you want to do | Command | Example |
|------------|----------|------|
| List all industries | `eastmoney list` | `eastmoney list` |
| Search industry | `eastmoney list -s keyword` | `eastmoney list -s 游戏` |
| Query reports | `eastmoney query` | See examples above |
| Download PDF | `eastmoney download` | See examples above |
| Export to CSV | `eastmoney query --save-csv` | `eastmoney query -i 1046 --save-csv` |

| 你想做什么 | 用的命令 | 例子 |
|------------|----------|------|
| 列出所有行业 | `report list` | `report list` |
| 搜索行业 | `report list -s 关键词` | `report list -s 游戏` |
| 查询研报 | `report query` | 见上面的例子 |
| 下载PDF | `report download` | 见上面的例子 |
| 导出Excel | `report query --save-csv` | `report query -i 1046 --save-csv` |

### 常用参数 | Common Parameters

| Parameter | Meaning | Usage |
|------|----------|--------|
| `-t` | Report type | `-t industry`, `-t strategy`, `-t stock` |
| `-i` | Industry code | `-i 1046` (gaming), `-i 1001` (agriculture) |
| `-c` | Stock code | `-c 600519` (Moutai), `-c 000001` (Ping An) |
| `-s` | Number of reports | `-s 5` (5 reports), `-s 20` (20 reports) |
| `-o` | Output directory | `-o ./reports` |
| `--save-csv` | Save as CSV | Add to query command |

| 参数 | 什么意思 | 怎么用 |
|------|----------|--------|
| `-t` | 研报类型 | `-t industry`（行业）、`-t strategy`（策略）、`-t stock`（个股） |
| `-i` | 行业代码 | `-i 1046`（游戏）、`-i 1001`（农业） |
| `-c` | 股票代码 | `-c 600519`（茅台）、`-c 000001`（平安） |
| `-s` | 要几条 | `-s 5`（5条）、`-s 20`（20条） |
| `-o` | 保存到哪 | `-o ./reports`（当前目录的reports文件夹） |
| `--save-csv` | 存为Excel | 加在query命令后面就行 |

### 研报类型对照表 | Report Types

| Type | Usage | Example |
|------|------|------|
| `industry` | Industry analysis | Gaming, healthcare, new energy |
| `strategy` | Market strategy | Market trends, investment advice |
| `macro` | Macro research | GDP, CPI, monetary policy |
| `morning` | Broker morning notes | Daily market updates |
| `stock` | Individual stock analysis | Moutai, Tencent |

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
report list

# 搜索包含"游戏"的行业
report list -s 游戏
```

### Q: 股票代码怎么查？
注意：接口不支持港股研报
直接用股票代码即可，比如：
- 茅台 = 600519
- 平安 = 000001

---

## 文件结构 | File Structure

```
eastmoney/
├── pyproject.toml      # Package configuration
├── MANIFEST.in         # Include data files
├── README.md           # Documentation
├── LICENSE             # MIT License
├── src/
│   └── eastmoney/
│       ├── __init__.py     # Package init
│       ├── __main__.py     # Support python -m eastmoney
│       ├── cli.py          # Command-line interface
│       ├── report_client.py # Eastmoney API client
│       ├── utils.py        # Utility functions
│       ├── legacy.py       # Legacy compatibility
│       └── data/
│           └── industry.json # Industry code data
├── .github/
│   └── workflows/
│       └── publish.yml     # PyPI publish workflow
└── tests/              # Test directory
```

**After installation via pip:**
```
# Command-line tools available:
eastmoney list
report list  # (legacy alias)
```

---

## 注意事项

1. **合理使用**：不要短时间内大量下载，给服务器留条活路 😂
2. **仅供学习**：下载的PDF仅供个人研究学习使用
3. **更新提醒**：如果东方财富 API 变了工具用不了，可以提 Issue

---


## MCP Server Support | 支持 MCP 协议

This package includes an MCP (Model Context Protocol) server, allowing AI agents to query and download reports directly.

本包包含 MCP (Model Context Protocol) 服务器，允许 AI 智能体直接查询和下载研报。

### Quick Start with MCP | MCP 快速开始

After installation, the MCP server is available as a command-line tool:

安装后，MCP 服务器可作为命令行工具使用：

```bash
# Start MCP server | 启动 MCP 服务器
eastmoney-mcp
```

### Install via Prompt | 通过提示词安装

For AI agents that support prompt-based installation (e.g., Cursor, Cline), copy and paste this prompt:

对于支持提示词安装的 AI agent（如 Cursor、Cline），复制以下提示词：

```
Please install and configure the Eastmoney MCP server:

1. Install the package: pip install eastmoney-reports
2. Add this to my MCP config file (e.g., ~/.cursor/mcp.json or ~/.cline/mcp_config.json):
{
  "mcpServers": {
    "eastmoney": {
      "command": "eastmoney-mcp",
      "description": "Eastmoney Research Reports Tool"
    }
  }
}
3. Verify installation by running: eastmoney-mcp --version
```

### One-Line Install (like npx) | 一行安装（类似 npx）

Using pipx (similar to npx for Python):

使用 pipx（类似 Python 版的 npx）：

```bash
# Run without permanent installation | 无需安装直接运行
pipx run eastmoney-reports eastmoney-mcp
```

If you don't have pipx installed:

如果还没安装 pipx：

```bash
pip install pipx
pipx ensurepath
```

### Configure in AI Tools | 在 AI 工具中配置

**Claude Desktop / Cursor / Cline:**

Add to your MCP config file (e.g., `claude_desktop_config.json`):

添加到 MCP 配置文件（如 `claude_desktop_config.json`）：

```json
{
  "mcpServers": {
    "eastmoney": {
      "command": "eastmoney-mcp",
      "description": "Eastmoney Research Reports Tool"
    }
  }
}
```

**Available MCP Tools | MCP 工具列表：**
- `list_industries` - List all industries | 列出所有行业
- `query_reports` - Query research reports | 查询研报
- `download_reports` - Download PDF reports | 下载研报 PDF
- `get_industry_code` - Search industry by keyword | 按关键词搜索行业

## License

MIT License - 随便用，开心就好！

---

<div align="center">

**觉得好用？点个 ⭐ Star 支持一下！**

</div>

---
