---
name: create-skill
description: >
  创建和发布新的 Skill 的完整指南。
  包含 Skill 目录结构、SKILL.md 规范、脚本组织、打包流程等详细规则。
  适用场景：需要创建新的 Skill 来扩展系统功能的开发者。
  当用户提到 "创建skill"、"开发skill"、"新建skill"、"skill开发指南"、
  "skill规范"、"skill打包"、"技能开发" 等关键词时，必须使用本 skill。
---

# Skill 创建指南

## 概述

Skill 是可复用的、自包含的工具包，用于扩展系统功能。每个 Skill 包含：
- **文档** (`SKILL.md`) - 说明和使用指南
- **脚本** (`scripts/`) - 可执行的工具代码
- **参考资源** (`references/`) - 辅助文档和说明
- **打包** (`.skill` 文件) - 压缩归档，便于分发

---

## 第一部分：Skill 目录结构规范

### 1.1 标准目录结构

```
.github/skills/
├── your-skill/                      # Skill 名称（使用小写，用连字符分隔）
│   ├── SKILL.md                     # 必需：主文档文件
│   ├── scripts/                     # 必需：脚本目录
│   │   ├── main_script.py           # 主脚本
│   │   ├── helper.py                # 辅助脚本（可选）
│   │   └── pyproject.toml           # Python 依赖配置（如需要）
│   └── references/                  # 可选：参考资源目录
│       ├── README.md                # 使用说明
│       ├── EXAMPLES.md              # 使用示例
│       └── schema.json              # 数据结构定义（如需要）
```

### 1.2 目录命名规则

| 目录/文件 | 命名规则 | 说明 |
|---------|---------|------|
| Skill 文件夹 | 小写 + 连字符 (`my-skill`) | 不使用下划线，英文名称 |
| 主脚本 | 驼峰式 (`myScript.py`) 或 蛇形 (`my_script.py`) | 保持一致 |
| `SKILL.md` | 大写 | 固定文件名，必需 |
| `pyproject.toml` | 小写 | 固定文件名 |
| 其他文档 | 大写首字母 (`README.md`, `EXAMPLES.md`) | Markdown 文件 |

### 1.3 文件大小限制

| 文件类型 | 建议大小 | 说明 |
|---------|---------|------|
| 单个脚本 | < 10 MB | 超过此大小考虑分离 |
| 整个 Skill | < 50 MB | 最终打包后 |
| SKILL.md | < 100 KB | 文档应简洁清晰 |

---

## 第二部分：SKILL.md 文件规范

### 2.1 YAML 前置数据（Front Matter）

```yaml
---
name: your-skill                    # 必需：Skill 名称（全小写，用连字符）
description: >                      # 必需：描述（支持多行）
  简单的一句话描述。
  支持多行描述，包含主要功能。
  当用户提到相关关键词时何时使用此 Skill。
  可列出触发关键词如："协议转换"、"文件提取" 等。
---
```

**要求：**
- `name`: 必须与文件夹名称一致
- `description`: 清晰说明 Skill 的用途和触发条件

### 2.2 Markdown 内容结构

#### 必需的一级标题

```markdown
# Skill 名称

## 任务概述
- 简述 Skill 做什么
- 适用场景
- 主要功能

## 第一步：环境准备
- 列出所需工具（Python、uv、特定库等）
- 验证环境的命令

## 第二步：输入文件处理
- 说明输入文件的位置和格式
- 文件结构说明表格
- 复制/准备文件的脚本

## 第三步：执行主要操作
- 详细的命令示例
- 参数说明
- 常见选项

## 第四步：输出处理
- 输出文件说明
- 文件位置
- 验证方法

## 完整使用示例
- 至少 2-3 个真实场景示例
- 完整的命令和预期输出

## 命令参数详解
- 每个命令的完整说明表
- 参数解释

## 功能特性
- 列出主要特性（✅ 勾选框格式）

## 依赖
- 列表格式说明所有依赖
- 版本号要求

## 故障排除
- 常见问题和解决方案
- 调试技巧

## 参考资源
- 相关文档链接
```

#### 推荐的可选标题

```markdown
## 高级用法
## 性能优化
## 最佳实践
## 常见陷阱
## 相关 Skills
```

### 2.3 Markdown 格式规范

#### 代码块

```markdown
# 标注语言
\`\`\`bash
command example
\`\`\`

\`\`\`python
python code
\`\`\`
```

#### 表格（使用 Markdown 表格）

```markdown
| 列1 | 列2 | 列3 |
|-----|-----|-----|
| 值1 | 值2 | 值3 |
```

#### 列表格式

```markdown
### 项目列表
- 项目 1
- 项目 2
- 项目 3

### 编号列表
1. 第一步
2. 第二步
3. 第三步

### 嵌套列表
- 父项
  - 子项 1
  - 子项 2
```

#### 强调和链接

```markdown
**粗体** - 重要概念
*斜体* - 强调
`代码` - 内联代码
[链接文本](https://example.com) - 外部链接
```

---

## 第三部分：脚本开发规范

### 3.1 Python 脚本要求

#### 文件头

```python
#!/usr/bin/env python3
"""
模块说明：一句话描述

详细说明（可选）：
多行说明 Skill 的功能和用途。
"""

import sys
from pathlib import Path
```

#### 代码风格

- **编码**: UTF-8（包含中文）
- **缩进**: 4 个空格
- **行长**: 建议 88 字符（Black 格式）
- **命名**: 
  - 函数：`snake_case`
  - 类：`PascalCase`
  - 常数：`UPPER_CASE`

#### 依赖管理

在 `scripts/pyproject.toml` 中声明所有依赖：

```toml
[project]
name = "your-skill"
version = "0.1.0"
description = "Your skill description"
requires-python = ">=3.8"
dependencies = [
    "package1>=1.0.0",
    "package2>=2.0.0",
]

[tool.uv]
python-version = "3.11"
```

#### 必需的功能

- **错误处理**: 捕获异常，提供有意义的错误信息
- **日志**: 使用 `print()` 或 logging，便于调试
- **验证**: 检查输入文件存在性、格式有效性
- **返回值**: CLI 脚本应返回适当的退出码（0=成功，1=错误）

### 3.2 脚本示例：基础 CLI 脚本

```python
#!/usr/bin/env python3
"""
模板脚本：处理输入文件并生成输出
"""

import sys
from pathlib import Path

def validate_input(file_path: str) -> Path:
    """验证输入文件"""
    path = Path(file_path).resolve()
    if not path.exists():
        print(f"ERROR: File not found: {file_path}")
        sys.exit(1)
    if path.suffix.lower() != ".txt":
        print(f"ERROR: Expected .txt file, got {path.suffix}")
        sys.exit(1)
    return path

def process_file(input_path: Path, output_path: Path) -> None:
    """处理文件"""
    try:
        content = input_path.read_text(encoding="utf-8")
        result = content.upper()  # 示例：转换为大写
        output_path.write_text(result, encoding="utf-8")
        print(f"Success: Processed {input_path.name}")
        print(f"Output: {output_path}")
    except Exception as e:
        print(f"ERROR: {e!s}")
        sys.exit(1)

def main():
    """主入口"""
    if len(sys.argv) < 2:
        print("Usage: script.py <input_file> [output_file]")
        sys.exit(1)
    
    input_file = validate_input(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("output.txt")
    
    process_file(input_file, output_file)

if __name__ == "__main__":
    main()
```

### 3.3 脚本示例：Typer CLI 脚本

```python
#!/usr/bin/env python3
"""
使用 Typer 框架的现代化 CLI 脚本
"""

from pathlib import Path
from typing import Optional
import typer

app = typer.Typer(name="My Tool", help="Tool description")

@app.command()
def process(
    input_file: str = typer.Argument(..., help="Input file path"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
) -> None:
    """Process input file"""
    input_path = Path(input_file).resolve()
    
    if not input_path.exists():
        typer.secho(f"ERROR: File not found", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    
    typer.secho(f"Processing: {input_path.name}", fg=typer.colors.CYAN)
    
    # 处理逻辑
    result = "processed content"
    
    if output_file:
        Path(output_file).write_text(result, encoding="utf-8")
        typer.secho(f"Output saved to: {output_file}", fg=typer.colors.GREEN)

if __name__ == "__main__":
    app()
```

---

## 第四部分：参考资源文件规范

### 4.1 README.md（使用说明）

```markdown
# Your Skill Name

简单的使用说明和快速开始指南。

## 快速开始

最简单的使用方式示例。

## 常见用法

列出 3-5 个常见的使用场景。

## 更多信息

指向 SKILL.md 的完整文档。
```

### 4.2 EXAMPLES.md（使用示例）

```markdown
# 使用示例

## 示例 1：基础用法

代码示例 + 预期输出

## 示例 2：高级用法

更复杂的示例

## 示例 3：与其他 Skills 结合

展示如何与其他 Skills 配合使用
```

### 4.3 其他参考文件

- `schema.json` - 数据格式定义
- `config.example.toml` - 配置文件示例
- `API.md` - API 文档
- `CHANGELOG.md` - 版本更新记录

---

## 第五部分：打包为 .skill 文件

### 5.1 验证目录结构

```bash
# 检查必需的文件
ls -la .github/skills/your-skill/
# 应该显示：
# - SKILL.md (必需)
# - scripts/ (必需)
# - references/ (可选)
```

### 5.2 打包命令

使用 7z 创建 .skill 文件（本质上是 ZIP 格式）：

```bash
cd .github/skills

# 创建 .skill 文件
7z a -tzip your-skill.skill your-skill\*

# 验证
7z l your-skill.skill
```

### 5.3 .skill 文件验证

```bash
# 检查文件大小
dir your-skill.skill

# 列出内容
7z l your-skill.skill

# 测试解压
mkdir test-extract
7z x your-skill.skill -otest-extract\

# 验证关键文件存在
ls test-extract/your-skill/SKILL.md
ls test-extract/your-skill/scripts/
```

### 5.4 分发和安装

```bash
# 复制 .skill 文件到发布目录
cp your-skill.skill /path/to/distribution/

# 用户安装（解压到 skills 目录）
7z x your-skill.skill -o.github/skills/
```

---

## 第六部分：Skill 检查清单

### 必需项

- [ ] 文件夹名称使用小写 + 连字符
- [ ] 包含 `SKILL.md` 文件
- [ ] SKILL.md 包含 YAML 前置数据 (name, description)
- [ ] 包含 `scripts/` 目录
- [ ] 至少有一个可执行脚本
- [ ] 如有 Python 依赖，包含 `scripts/pyproject.toml`
- [ ] SKILL.md 包含所有必需的章节（见 2.2）
- [ ] 至少包含 2-3 个完整的使用示例
- [ ] 所有代码注释为英文或中文（保持一致）

### 推荐项

- [ ] 包含 `references/README.md` 快速开始指南
- [ ] 包含 `references/EXAMPLES.md` 详细示例
- [ ] 脚本包含彩色输出（提升用户体验）
- [ ] 包含故障排除部分
- [ ] 包含参考资源链接
- [ ] 代码通过 linting 检查
- [ ] 文档中有清晰的表格和列表

### 质量指标

| 指标 | 目标 |
|------|------|
| SKILL.md 行数 | 100-500 行 |
| 代码注释率 | > 20% |
| 单个脚本大小 | < 1000 行 |
| 示例数量 | 3+ 个 |
| 错误处理 | 100% |

---

## 第七部分：常见 Skill 模板

### 模板 1：数据转换 Skill

```
特点：输入文件 → 转换 → 输出文件
示例：CSV → DBC、PDF → CSV 等

必需部分：
- 输入文件验证
- 转换逻辑
- 输出文件生成
```

### 模板 2：分析工具 Skill

```
特点：输入文件 → 分析 → 报告
示例：PDF 总结、代码分析等

必需部分：
- 文件解析
- 统计分析
- 报告生成
```

### 模板 3：管理工具 Skill

```
特点：命令行工具管理系统资源
示例：Skill 管理器、项目运行器等

必需部分：
- 命令定义
- 参数处理
- 结果反馈
```

### 模板 4：集成工具 Skill

```
特点：协调其他 Skills 或工具
示例：UV 项目运行器等

必需部分：
- 环境检查
- 工具集成
- 流程管理
```

---

## 第八部分：最佳实践

### 8.1 文档编写

✅ **好的做法：**
```markdown
## 第一步：环境准备

使用 uv 安装依赖：

\`\`\`bash
uv run script.py --help
\`\`\`

输出应显示命令帮助信息。
```

❌ **不好的做法：**
```markdown
安装依赖。

运行脚本。
```

### 8.2 脚本开发

✅ **好的做法：**
```python
def process_file(path: str) -> None:
    """验证并处理文件"""
    file_path = Path(path).resolve()
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    # 处理逻辑
```

❌ **不好的做法：**
```python
def process(f):
    # 处理
    pass
```

### 8.3 错误处理

✅ **包含详细错误信息：**
```bash
ERROR: Input file not found: /path/to/file.txt
Expected file format: .pdf or .xlsx
```

❌ **模糊的错误：**
```bash
Error!
```

### 8.4 示例补充度

✅ **完整的示例：**
```bash
$ uv run script.py input.pdf
Processing: input.pdf
Total pages: 7
[STATISTICS]
Total text: 4038 characters
```

❌ **不完整的示例：**
```bash
$ uv run script.py
# 没有输出说明
```

---

## 第九部分：版本管理和更新

### 9.1 版本号规范

遵循 Semantic Versioning (SemVer)：`MAJOR.MINOR.PATCH`

```toml
# pyproject.toml
version = "0.1.0"  # 初始版本
# version = "1.0.0"  # 首个稳定版本
# version = "1.1.0"  # 新功能
# version = "1.1.1"  # Bug 修复
```

### 9.2 SKILL.md 版本

在 SKILL.md 顶部添加版本标记：

```markdown
---
name: your-skill
version: 0.1.0
description: >
  ...
---
```

### 9.3 更新记录

在 `references/CHANGELOG.md` 记录：

```markdown
# 更新记录

## [1.0.0] - 2026-03-11

### Added
- 新功能说明

### Fixed
- Bug 修复说明

### Changed
- 改动说明
```

---

## 第十部分：故障排除和调试

### 问题：Skill 文件打包失败

```bash
# 检查目录存在
test -d .github/skills/your-skill

# 检查关键文件
test -f .github/skills/your-skill/SKILL.md
test -d .github/skills/your-skill/scripts

# 尝试手动创建
7z a -tzip your-skill.skill ".github/skills/your-skill"
```

### 问题：脚本中文输出乱码

```python
# 确保文件编码
import sys
sys.stdout.reconfigure(encoding='utf-8')  # Python 3.7+

# 或在脚本顶部
# -*- coding: utf-8 -*-
```

### 问题：导入模块找不到

```bash
# 验证 pyproject.toml 中的依赖
cat scripts/pyproject.toml

# 重新运行 uv 安装
cd scripts
uv sync
```

---

## 参考资源

- [YAML 格式](https://yaml.org/)
- [Markdown 语法](https://commonmark.org/)
- [Python PEP 8 风格指南](https://pep8.org/)
- [Semantic Versioning](https://semver.org/)
- [7z 压缩工具](https://www.7-zip.org/)

---

## 快速参考

### 创建新 Skill 的最小步骤

```bash
# 1. 创建目录结构
mkdir -p .github/skills/my-skill/scripts
mkdir -p .github/skills/my-skill/references

# 2. 创建必需文件
touch .github/skills/my-skill/SKILL.md
touch .github/skills/my-skill/scripts/main.py
touch .github/skills/my-skill/scripts/pyproject.toml

# 3. 编写文件内容
# ... 按照规范编写 SKILL.md 和脚本

# 4. 打包
cd .github/skills
7z a -tzip my-skill.skill my-skill\*

# 5. 验证
7z l my-skill.skill
```

---

## 获取帮助

- 参考本文档的各个部分
- 查看现有 Skills 的实现示例
- 测试脚本：在发布前充分测试
- 文档验证：使用 Markdown linter 检查格式
