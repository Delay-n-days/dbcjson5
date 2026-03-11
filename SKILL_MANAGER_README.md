# Skill 管理工具 - Typer 版本

一个功能强大的 CLI 工具，用于管理 `.skill` 文件（7z 压缩格式）。

## 特性

✨ 使用 [Typer](https://typer.tiangolo.com/) 框架创建的现代 CLI 工具

- 📦 **安装** Skill 文件
- 📋 **列出** 已安装的 Skill
- ℹ️ **查看** Skill 的详细信息
- 🔄 **更新** 已安装的 Skill
- 🗑️ **删除** 已安装的 Skill

## 安装依赖

```bash
# 安装 typer
pip install typer

# 可选：安装 py7zr（推荐，无需依赖 7z 命令行工具）
pip install py7zr
```

## 使用方法

### 显示帮助

```bash
python skill_manager.py --help
```

### 1. 📦 安装 Skill

安装一个新的 Skill 文件：

```bash
# 基本使用
python skill_manager.py install pdf-to-can-csv.skill

# 强制覆盖（跳过确认）
python skill_manager.py install pdf-to-can-csv.skill --force

# 详细输出
python skill_manager.py install pdf-to-can-csv.skill --verbose

# 指定基础目录
python skill_manager.py install pdf-to-can-csv.skill --base-dir /path/to/project
```

**选项:**

- `--base-dir`, `-b` : 指定基础目录（默认：当前目录）
- `--force`, `-f` : 强制覆盖，跳过确认提示
- `--verbose`, `-v` : 显示详细的操作过程

### 2. 📋 列出已安装的 Skill

```bash
# 列出所有已安装的 Skill
python skill_manager.py list-skills

# 指定基础目录
python skill_manager.py list-skills --base-dir /path/to/project
```

输出示例：

```
📦 已安装的 Skill (3):

  1. can-matrix-to-json5            [✓]
  2. can-protocol-to-json5          [✓]
  3. pdf-to-can-csv                 [✓]
```

### 3. ℹ️ 查看 Skill 详细信息

```bash
# 查看 Skill 的详细信息
python skill_manager.py info pdf-to-can-csv

# 指定基础目录
python skill_manager.py info pdf-to-can-csv --base-dir /path/to/project
```

输出示例：

```
📦 Skill 信息: pdf-to-can-csv

位置: C:\Users\25156\Desktop\dbcjson5\.github\skills\pdf-to-can-csv
文件数: 3

📄 包含的文件:
  - references\csv_output_template.md
  - references\unified_csv_format.md
  - SKILL.md
```

### 4. 🔄 更新 Skill

更新已安装的 Skill（自动覆盖）：

```bash
# 更新 Skill
python skill_manager.py update pdf-to-can-csv.skill

# 详细输出
python skill_manager.py update pdf-to-can-csv.skill --verbose

# 指定基础目录
python skill_manager.py update pdf-to-can-csv.skill --base-dir /path/to/project
```

### 5. 🗑️ 删除 Skill

```bash
# 删除 Skill（需要确认）
python skill_manager.py remove pdf-to-can-csv

# 强制删除（跳过确认）
python skill_manager.py remove pdf-to-can-csv --force

# 指定基础目录
python skill_manager.py remove pdf-to-can-csv --base-dir /path/to/project
```

### 显示版本

```bash
python skill_manager.py --version
```

## 常见用法

### 创建 CLI 别名（可选）

#### Windows (PowerShell)

```powershell
# 添加到 PowerShell 配置文件
function skill { python C:\path\to\skill_manager.py @args }
```

#### Linux/macOS

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
alias skill="python /path/to/skill_manager.py"

# 重新加载配置
source ~/.bashrc
```

之后可以直接使用：

```bash
skill list-skills
skill install pdf-to-can-csv.skill
skill info pdf-to-can-csv
```

## 工作流程示例

```bash
# 1. 列出所有已安装的 Skill
python skill_manager.py list-skills

# 2. 查看某个 Skill 的信息
python skill_manager.py info pdf-to-can-csv

# 3. 安装新的 Skill
python skill_manager.py install my-new-skill.skill

# 4. 更新已安装的 Skill
python skill_manager.py update pdf-to-can-csv.skill

# 5. 删除不需要的 Skill
python skill_manager.py remove my-skill
```

## 文件结构

安装完成后，Skill 将被放在以下位置：

```
project/
├── .github/
│   └── skills/
│       ├── can-matrix-to-json5/
│       ├── can-protocol-to-json5/
│       ├── pdf-to-can-csv/
│       │   ├── SKILL.md
│       │   ├── references/
│       │   └── ...
│       └── ...
└── ...
```

## 错误处理

工具会提供清晰的错误消息：

```
❌ Skill 'my-skill' 不存在
❌ 文件类型错误，应为.skill文件
❌ Skill文件不存在
```

## 交互式确认

覆盖和删除操作会要求用户确认：

```bash
📂 已找到现有Skill: .github\skills\pdf-to-can-csv

⚠️  Skill 'pdf-to-can-csv' 已存在。是否替换/升级？(y/n): y
```

可以使用 `--force` 或 `-f` 标志跳过确认：

```bash
python skill_manager.py install pdf-to-can-csv.skill --force
python skill_manager.py remove pdf-to-can-csv --force
```

## Typer 特性

此工具使用 Typer 框架，提供：

- 🎨 彩色输出和格式化的帮助信息
- ⌨️ 完整的 tab 补全支持
- 📚 自动生成的帮助文档
- 🔍 清晰的参数和选项验证
- 💪 类型提示和自动文档

## 许可

根据项目许可证。

## 相关资源

- [Typer 官方文档](https://typer.tiangolo.com/)
- [原始脚本](install_skill.py)
