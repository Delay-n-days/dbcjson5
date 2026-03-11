## 快速开始：创建你的第一个 Skill

### 第 1 步：准备目录结构

```bash
# 创建 Skill 目录（使用小写 + 连字符）
mkdir -p .github/skills/my-first-skill/scripts
mkdir -p .github/skills/my-first-skill/references
```

### 第 2 步：创建 SKILL.md

在 `.github/skills/my-first-skill/SKILL.md` 中写入：

```yaml
---
name: my-first-skill
description: >
  我的第一个 Skill：执行简单的数据处理任务。
  支持输入验证、数据转换、输出生成。
  当用户需要处理数据文件时使用此 Skill。
---

# 我的第一个 Skill

## 任务概述

此 Skill 演示如何创建一个完整的、可复用的工具。

## 第一步：环境准备

需要 Python 3.8+ 和 uv 工具。

## 第二步：使用方法

\`\`\`bash
uv run main.py input.txt
\`\`\`

## 完整示例

\`\`\`bash
$ uv run main.py data.txt
Processing: data.txt
Success: Output saved to output.txt
\`\`\`

## 参考资源

详见完整的创建 Skill 指南。
```

### 第 3 步：创建脚本

在 `.github/skills/my-first-skill/scripts/main.py` 中写入：

```python
#!/usr/bin/env python3
"""
我的第一个 Skill 脚本
"""

import sys
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Usage: main.py <input_file>")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    if not input_file.exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)
    
    print(f"Processing: {input_file.name}")
    
    # 你的处理逻辑
    content = input_file.read_text()
    result = content.upper()
    
    output_file = input_file.stem + "_output.txt"
    Path(output_file).write_text(result)
    
    print(f"Success: Output saved to {output_file}")

if __name__ == "__main__":
    main()
```

### 第 4 步：创建 pyproject.toml

在 `.github/skills/my-first-skill/scripts/pyproject.toml` 中写入：

```toml
[project]
name = "my-first-skill"
version = "0.1.0"
description = "My first skill"
requires-python = ">=3.8"
dependencies = []

[tool.uv]
python-version = "3.11"
```

### 第 5 步：创建 references/README.md

在 `.github/skills/my-first-skill/references/README.md` 中写入：

```markdown
# My First Skill - 快速开始

## 简单用法

```bash
cd .github/skills/my-first-skill/scripts
uv run main.py input.txt
```

## 更多信息

详见 SKILL.md
```

### 第 6 步：打包为 .skill 文件

```bash
cd .github/skills
7z a -tzip my-first-skill.skill my-first-skill\*
```

### 第 7 步：验证

```bash
# 检查文件内容
7z l my-first-skill.skill

# 输出应包含：
# - my-first-skill\SKILL.md
# - my-first-skill\scripts\main.py
# - my-first-skill\scripts\pyproject.toml
# - my-first-skill\references\README.md
```

---

## Skill 目录结构检查清单

使用此清单确保你的 Skill 结构完整：

```
my-first-skill/
├── SKILL.md                      ✅ 必需
│   ├── YAML 前置数据 (name, description)
│   ├── # 标题和内容
│   ├── 任务概述
│   ├── 使用步骤
│   └── 完整示例
├── scripts/                      ✅ 必需
│   ├── main.py                   ✅ 至少一个脚本
│   └── pyproject.toml            (如有依赖)
└── references/                   ⭐ 推荐
    ├── README.md                 ⭐ 快速开始
    └── EXAMPLES.md               ⭐ 详细示例
```

---

## 常见错误和修复

### ❌ 错误 1：SKILL.md 的 YAML 格式不正确

```yaml
# 错误：不在代码块中
name: my-skill
description: My skill

# 正确：在 --- 之间
---
name: my-skill
description: My skill
---
```

### ❌ 错误 2：脚本路径错误

```bash
# 错误
7z a my-skill.skill my-skill

# 正确
cd .github/skills
7z a my-skill.skill my-skill\*
```

### ❌ 错误 3：缺少 pyproject.toml

如果脚本有外部依赖，**必须** 包含 `scripts/pyproject.toml`。

```toml
dependencies = [
    "package-name>=1.0.0",
]
```

---

## 示例：完整的 csv-to-dbc Skill

查看实际的 Skill 实现：

```bash
# 查看现有 Skill 的结构
ls -R .github/skills/csv-to-dbc/

# 查看完整的 SKILL.md
cat .github/skills/csv-to-dbc/SKILL.md
```

---

## 发布你的 Skill

### 步骤 1：检查清单

- [ ] 所有文件创建完毕
- [ ] SKILL.md 包含完整内容
- [ ] 脚本已测试
- [ ] 文件夹和文件名都是小写（除了特定的大写文件）

### 步骤 2：打包

```bash
cd .github/skills
7z a -tzip your-skill.skill your-skill\*
```

### 步骤 3：验证

```bash
7z l your-skill.skill
```

### 步骤 4：分发

将 `.skill` 文件分享给其他用户。

---

## 获取更多帮助

- 📖 查看完整指南：SKILL.md
- 🔍 参考现有 Skills：`csv-to-dbc`, `pdf-summary` 等
- 🐛 调试技巧：见 SKILL.md 的故障排除章节
