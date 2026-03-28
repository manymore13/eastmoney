# 东方财富研报下载工具

命令行工具，用于查询和下载东方财富的研究报告（行业研报、策略报告、宏观研究、券商晨报、个股研报）。

支持 macOS、Linux、Windows 系统。

## 功能特性

- 📋 查询研报列表（支持多种类型）
- 📥 下载研报 PDF 文件
- 📊 导出 CSV 数据
- 🔍 搜索行业
- 🚀 跨平台支持（Windows/macOS/Linux）

## 环境要求

- Python 3.8+
- curl（系统自带）

## 安装

```bash
# 克隆项目
git clone https://github.com/yourusername/eastmoney-reports.git
cd eastmoney-reports

# 安装依赖
pip install -r requirements.txt
```

## 使用方法

### Windows

```bash
# 列出行业
report list
report list -s 游戏

# 查询研报
report query -t industry -i 1046 -s 20
report query -t strategy -s 10
report query -t macro -s 10
report query -t stock -c 600519 -s 10

# 下载研报 PDF
report download -t industry -i 1046 -s 5 -o ./reports
report download -t strategy -s 3 -o ./reports

# 导出 CSV
report query -t strategy -s 10 --save-csv
```

### macOS / Linux

```bash
# 先添加执行权限
chmod +x report

# 使用方式与 Windows 相同
./report list
./report query -t strategy -s 5
./report download -t industry -i 1046 -o ./reports
```

## 命令说明

| 命令 | 说明 |
|------|------|
| `report list` | 列出所有行业 |
| `report query` | 查询研报列表 |
| `report download` | 下载研报 PDF |

## 参数说明

| 参数 | 简写 | 说明 | 示例 |
|------|------|------|------|
| `--type` | `-t` | 研报类型 | `industry`, `stock`, `strategy`, `macro`, `morning` |
| `--industry` | `-i` | 行业代码 | `1046` |
| `--code` | `-c` | 股票代码 | `600519` |
| `--page` | `-p` | 页码 | `1` |
| `--pagesize` | `-s` | 每页数量 | `20` |
| `--output` | `-o` | 输出目录 | `./reports` |
| `--begin` | | 开始日期 | `2026-01-01` |
| `--end` | | 结束日期 | `2026-03-28` |
| `--save-csv` | | 保存为CSV | |
| `--all` | | 下载所有行业 | |

## 研报类型说明

- `industry` - 行业研报
- `stock` - 个股研报
- `strategy` - 策略报告
- `macro` - 宏观研究
- `morning` - 券商晨报

## 输出目录

下载的 PDF 文件保存在：
```
./reports/
├── industry/      # 行业研报
├── strategy/      # 策略报告
├── macro/         # 宏观研究
├── morning/       # 券商晨报
└── [股票代码]/    # 个股研报
```

## 常见问题

### 1. PDF 下载失败？

确保已安装 curl：
```bash
# macOS
brew install curl

# Linux
sudo apt install curl  # Debian/Ubuntu
sudo yum install curl # RHEL/CentOS
```

### 2. 如何获取行业代码？

```bash
report list
```

## 注意事项

- 请合理使用，避免对东方财富服务器造成压力
- 下载的 PDF 仅供个人学习研究使用
- 如遇 API 变更，请提交 Issue

## License

MIT License
