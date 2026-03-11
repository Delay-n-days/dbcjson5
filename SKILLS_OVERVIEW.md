# 已创建的 Skill 概览

## 📦 Skill 文件列表

### 1. pdf-summary.skill (6.5 KB)

**用途**：提取并总结 CAN 通讯协议 PDF 文档

**包含内容**：
- `SKILL.md` - 详细使用指南
- `scripts/summarize_pdf.py` - 基于 Typer 框架的 CLI 工具
- `scripts/pyproject.toml` - 依赖配置
- `references/README.md` - 快速开始指南

**主要功能**：
- ✅ 完整的文本提取
- ✅ 统计分析（总页数、字符数）
- ✅ 关键词搜索
- ✅ 自定义搜索关键词支持
- ✅ 输出到文件选项

**依赖**：
- `pdfplumber>=0.10.0`
- `typer>=0.9.0`

**使用示例**：
```bash
cd .github/skills/pdf-summary/scripts
uv run summarize_pdf.py summarize "../protocol.pdf" --no-content
```

---

### 2. create-skill.skill (12.7 KB)

**用途**：完整的 Skill 创建和开发指南

**包含内容**：
- `SKILL.md` - 详细的规范和开发指南（1000+ 行）
- `references/QUICKSTART.md` - 快速开始指南
- `references/CHECKLIST.md` - 开发检查清单
- `scripts/template.py` - Skill 脚本模板
- `scripts/pyproject.toml` - 依赖配置

**主要章节**：
1. Skill 目录结构规范
2. SKILL.md 文件规范
3. 脚本开发规范
4. 参考资源文件规范
5. 打包为 .skill 文件
6. Skill 检查清单
7. 常见 Skill 模板
8. 最佳实践
9. 版本管理
10. 故障排除和调试

**使用场景**：
- 想要创建新 Skill 的开发者
- 需要参考 Skill 规范的团队
- 学习 Skill 最佳实践

**快速查阅**：
1. `QUICKSTART.md` - 5 分钟快速上手
2. `SKILL.md` - 完整的详细指南
3. `CHECKLIST.md` - 开发清单和检查表
4. `template.py` - 脚本模板代码

---

## 📂 目录结构

```
.github/skills/
├── create-skill/                    # Skill 创建指南
│   ├── SKILL.md                     # 主文档（详细规范）
│   ├── scripts/
│   │   ├── template.py              # 脚本模板
│   │   └── pyproject.toml
│   └── references/
│       ├── QUICKSTART.md            # 快速开始
│       └── CHECKLIST.md             # 检查清单
├── pdf-summary/                     # PDF 总结工具
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── summarize_pdf.py         # CLI 工具
│   │   └── pyproject.toml
│   └── references/
│       └── README.md
├── create-skill.skill               # 打包文件
└── pdf-summary.skill                # 打包文件
```

---

## 🚀 快速开始

### 查看 Skill 创建指南

```bash
# 解压 create-skill.skill
7z x create-skill.skill

# 阅读快速开始
cat create-skill/references/QUICKSTART.md

# 查看完整指南
cat create-skill/SKILL.md

# 参考脚本模板
cat create-skill/scripts/template.py

# 使用开发清单
cat create-skill/references/CHECKLIST.md
```

### 使用 PDF 总结工具

```bash
# 解压 pdf-summary.skill
7z x pdf-summary.skill

# 进入 scripts 目录
cd pdf-summary/scripts

# 查看帮助
uv run summarize_pdf.py --help

# 总结 PDF
uv run summarize_pdf.py summarize "your_file.pdf"

# 提取文本
uv run summarize_pdf.py extract-text "your_file.pdf" -o output.txt
```

---

## 📋 Skill 对比表

| 特性 | create-skill | pdf-summary |
|------|-------------|------------|
| **用途** | 创建 Skill 的指南 | PDF 提取工具 |
| **文档长度** | 1000+ 行 | 200+ 行 |
| **代码行数** | 100+ 行 | 170+ 行 |
| **依赖数** | 0 | 2 |
| **文件大小** | 12.7 KB | 6.5 KB |
| **脚本数** | 1 | 1 |
| **参考文档** | 2 | 1 |
| **示例数量** | 5+ | 3+ |
| **适用对象** | 开发者 | 用户 |

---

## 🎯 使用场景

### 场景 1：创建新的 Skill

1. 阅读 `create-skill` 中的 `QUICKSTART.md`
2. 参考 `template.py` 开发脚本
3. 按照 `CHECKLIST.md` 检查完整性
4. 参考 `SKILL.md` 编写文档
5. 打包为 `.skill` 文件

### 场景 2：提取 PDF 文档

1. 使用 `pdf-summary` Skill
2. 运行 `summarize` 命令提取内容
3. 或使用 `extract-text` 命令提取纯文本
4. 支持关键词搜索和统计分析

### 场景 3：学习 Skill 开发

1. 研究 `pdf-summary` 的完整实现
2. 阅读 `create-skill` 的详细规范
3. 对比代码和文档
4. 参考 `template.py` 开发自己的 Skill

---

## 📖 文档导览

### 快速查阅（5-10 分钟）

| 需要 | 查看文档 |
|------|---------|
| 快速创建 Skill | `create-skill/references/QUICKSTART.md` |
| PDF 工具快速开始 | `pdf-summary/references/README.md` |
| 查看脚本模板 | `create-skill/scripts/template.py` |

### 深入学习（30+ 分钟）

| 需要 | 查看文档 |
|------|---------|
| Skill 完整规范 | `create-skill/SKILL.md` |
| PDF 工具详细指南 | `pdf-summary/SKILL.md` |
| 开发检查清单 | `create-skill/references/CHECKLIST.md` |

### 实践参考（边学边做）

| 需要 | 查看文档 |
|------|---------|
| 开发新 Skill | 参考 `pdf-summary` 的完整实现 |
| 编写脚本 | 使用 `create-skill/scripts/template.py` |
| 验证完整性 | 使用 `create-skill/references/CHECKLIST.md` |

---

## 🔗 关联资源

### 现有 Skills（系统内置）

- `csv-to-dbc` - CSV 转 DBC 文件
- `pdf-to-can-csv` - PDF 转 Unified CSV
- `uv-project-runner` - uv 项目运行器
- `skill-manager` - Skill 管理工具

### 创建的 Skills

- `pdf-summary` - PDF 提取工具（本次新建）
- `create-skill` - Skill 创建指南（本次新建）

---

## 💡 建议

1. **新手开发者**：先阅读 `create-skill/references/QUICKSTART.md`
2. **参考实现**：查看 `pdf-summary` 的完整代码和文档
3. **规范遵循**：使用 `create-skill/references/CHECKLIST.md` 检查
4. **模板使用**：复用 `create-skill/scripts/template.py` 作为起点

---

## 📞 获取帮助

- 📖 查看完整文档：`create-skill/SKILL.md`
- ⚡ 快速开始：`create-skill/references/QUICKSTART.md`
- ✅ 检查清单：`create-skill/references/CHECKLIST.md`
- 💻 脚本模板：`create-skill/scripts/template.py`

---

**最后更新**：2026-03-11
**创建者**：GitHub Copilot
