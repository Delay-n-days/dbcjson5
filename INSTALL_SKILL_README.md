# Skill 文件安装脚本

这是一个用于安装 `.skill` 文件的 Python 脚本。

## 功能说明

该脚本执行以下操作：

1. **解压 Skill 文件**：使用 7z 解压 `.skill` 文件（7z 压缩格式）到临时目录
2. **创建目标目录**：如果 `.github/skills/` 目录不存在，自动创建
3. **检查已有 Skill**：如果目标 Skill 已存在，提示用户是否覆盖/升级
4. **安装 Skill**：将 Skill 文件夹复制到 `.github/skills/` 目录

## 使用方法

### 基本使用

```bash
python install_skill.py <skill_file_path>
```

### 示例

```bash
# 安装当前目录下的 Skill 文件
python install_skill.py pdf-to-can-csv.skill

# 安装指定路径的 Skill 文件
python install_skill.py ./path/to/my-skill.skill
```

## 依赖要求

### 必需

- **Python 3.6+**
- **7z 命令行工具**（用于解压 Skill 文件）

### 可选

- **py7zr**（Python 库，如果已安装，将优先使用，无需 7z 命令行工具）
  
  ```bash
  pip install py7zr
  ```

## 安装流程

### 首次安装（Skill 不存在）

```bash
$ python install_skill.py pdf-to-can-csv.skill

🔧 开始安装Skill文件...
📍 临时目录: C:\Users\25156\AppData\Local\Temp\tmpXXXX
📦 正在解压: pdf-to-can-csv.skill
✅ 解压成功
📌 Skill名称: pdf-to-can-csv
📁 目标目录: .github\skills
📋 复制到目标位置...
✅ Skill安装成功！
📍 安装位置: C:\Users\25156\Desktop\dbcjson5\.github\skills\pdf-to-can-csv
```

### 升级已有的 Skill

如果 Skill 已存在，脚本会提示用户：

```bash
$ python install_skill.py pdf-to-can-csv.skill

🔧 开始安装Skill文件...
...
📂 已找到现有Skill: .github\skills\pdf-to-can-csv

⚠️  Skill 'pdf-to-can-csv' 已存在。是否替换/升级？(y/n): y
🗑️  移除旧版本...
📋 复制到目标位置...
✅ Skill安装成功！
```

## 错误处理

脚本会提供详细的错误消息：

- **文件不存在**：提示 Skill 文件不存在
- **文件类型错误**：提示文件必须为 `.skill` 格式
- **解压失败**：提示 7z 解压失败，通常是因为缺少 7z 工具
- **权限错误**：提示没有足够的权限创建或修改目录

## 文件结构

安装后，Skill 文件夹将被放在 `.github/skills/` 目录下：

```
project/
├── .github/
│   └── skills/
│       └── pdf-to-can-csv/
│           ├── SKILL.md
│           ├── references/
│           └── ...
└── ...
```

## 注意事项

- **临时文件**：脚本使用系统临时目录，在安装完成后会自动清理
- **覆盖确认**：升级现有 Skill 时，脚本会要求用户确认
- **跨平台支持**：脚本支持 Windows、macOS 和 Linux

## 代码结构

### 主要函数

- `extract_skill_file()`：解压 Skill 文件
- `get_skill_name()`：获取 Skill 名称
- `get_target_skills_dir()`：获取/创建目标目录
- `prompt_overwrite()`：提示用户是否覆盖
- `install_skill()`：主安装流程
- `main()`：入口函数

## 许可

根据项目许可证。
