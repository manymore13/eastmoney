# PyPI Publishing Plan for eastmoney-reports

## 1. Project Restructure (Convert to Standard Python Package)

**New Directory Structure:**
```
eastmoney/
├── pyproject.toml
├── MANIFEST.in
├── src/
│   └── eastmoney/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── report_client.py
│       ├── utils.py
│       └── data/
│           └── industry.json
├── tests/
└── .github/workflows/
    └── publish.yml
```

**Changes to existing files:**
- In `cli.py`, `report_client.py`, `utils.py`: update imports to `from eastmoney import ...`
- In `report_client.py` and `eastmoney.py`: use `importlib.resources` to read `industry.json`

---

## 2. `pyproject.toml` (Full English, No Chinese)

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "eastmoney-reports"
version = "1.0.0"
description = "Tool for querying and downloading Eastmoney research reports"
readme = "README.md"
license = {text = "MIT"}
authors = [
    {name = "Community Template"},
]
keywords = ["eastmoney", "financial", "research-reports", "stock", "market-analysis"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Financial and Insurance Industry",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]
requires-python = ">=3.8"
dependencies = [
    "requests>=2.28.0",
    "lxml>=4.9.0",
]

[project.optional-dependencies]
mcp = ["fastmcp>=0.1.0"]

[project.scripts]
eastmoney = "eastmoney.cli:main"
report = "eastmoney.cli:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
"eastmoney" = ["data/*.json"]
```

---

## 3. `MANIFEST.in`

```
include src/eastmoney/data/industry.json
include README.md
include LICENSE
```

---

## 4. GitHub Action Workflow `.github/workflows/publish.yml`

```yaml
name: Publish to PyPI

on:
  push:
    tags:
      - 'v*'

jobs:
  publish:
    runs-on: ubuntu-latest
    environment: pypi
    permissions:
      id-token: write
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install build dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine
      
      - name: Build package
        run: python -m build
      
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
```

---

## 5. User Configuration Steps

1. **Create PyPI account & API Token:**
   - Visit https://pypi.org/manage/account/
   - Create API Token (scope: entire account or specific project)
   - Copy token (starts with `pypi-`)

2. **Add Secret to GitHub Repository:**
   - Go to Settings → Secrets and variables → Actions
   - Click New repository secret
   - Name: `PYPI_API_TOKEN`
   - Secret: paste your PyPI API Token

3. **Publish:**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
