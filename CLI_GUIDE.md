#!/usr/bin/env python
"""
csv2dbc 命令行工具使用指南

这是一个基于 Typer 框架的 CSV 到 DBC 文件转换工具。
"""

# 快速开始

## 安装依赖

```bash
pip install typer cantools
```

## 基本用法

### 1. 查看帮助信息
```bash
python csv2dbc.py --help
```

输出主菜单和可用命令。

### 2. 查看转换命令帮助
```bash
python csv2dbc.py convert --help
```

### 3. 基本转换（使用默认编码 gb2312）
```bash
python csv2dbc.py convert "outputs/LvKong_1C_V2.5_A484_A485_100_00B_unified.csv"
```

**输出**：
- 自动生成到 `outputs/LvKong_1C_V2.5_A484_A485_100_00B_unified_from_unified.dbc`

### 4. 指定输出文件
```bash
python csv2dbc.py convert "data.csv" --output "result.dbc"
# 或简写
python csv2dbc.py convert "data.csv" -o "result.dbc"
```

### 5. 指定编码（如 UTF-8）
```bash
python csv2dbc.py convert "data.csv" --encoding "utf-8"
# 或简写
python csv2dbc.py convert "data.csv" -e utf-8
```

### 6. 同时指定输出和编码
```bash
python csv2dbc.py convert "data.csv" -o "output.dbc" -e utf-8
```

### 7. 查看版本
```bash
python csv2dbc.py version
```

## 完整参数说明

### convert 命令

**位置参数**：
- `UNIFIED_CSV` (必需): 统一 CSV 文件路径

**选项参数**：
- `-o, --output`: 输出 DBC 文件路径（可选，默认自动生成）
- `-e, --encoding`: CSV 文件编码（默认 gb2312）

## 常见用例

### 用例 1：转换工程项目中的 CSV
```bash
python csv2dbc.py "projects/car_dbc/unified.csv"
```

### 用例 2：批量转换多个 CSV
```bash
for csv_file in *.csv; do
    python csv2dbc.py "$csv_file"
done
```

### 用例 3：转换 UTF-8 编码的 CSV 到指定目录
```bash
python csv2dbc.py "data/input.csv" -o "dbc/output.dbc" -e utf-8
```

## 转换流程

1. **读取 CSV**：解析统一格式的 CSV 文件
2. **数据处理**：
   - 消息去重
   - 数据类型转换
   - 周期信息处理
   - 注释格式转换
3. **生成 DBC**：使用 cantools 生成 DBC 文件
4. **验证**：加载生成的 DBC 并验证消息数量

## 输出信息

成功转换输出示例：
```
正在读取统一 CSV: outputs/data_unified.csv
使用原始 DBC 文件作为模板: template.dbc
正在生成 DBC 文件...
正在写入 DBC 文件: outputs/data_unified_from_unified.dbc
正在验证生成的 DBC 文件...
✓ 验证成功! 包含 14 条消息
✓ 输出文件: outputs/data_unified_from_unified.dbc
```

## 错误处理

### 文件不存在
```
错误: 文件 data.csv 不存在
```

### 编码错误
确保 `--encoding` 参数与 CSV 文件实际编码一致。

## 进阶：创建可执行脚本

在 Windows 上，可以创建一个 `.bat` 文件来简化调用：

**csv2dbc.bat**
```batch
@echo off
python %~dp0csv2dbc.py %*
```

然后直接调用：
```bash
csv2dbc.bat convert "data.csv"
```

## 版本信息

- **工具版本**：v2.0
- **框架**：Typer 0.12.3+
- **依赖**：cantools
- **最后更新**：2026-03-11
