# Skill Manager

Skill 文件管理工具 - 使用 Typer 创建的 CLI 应用

## 使用方法

```bash
python scripts/skill.py --help
python scripts/skill.py install <skill_file>
python scripts/skill.py list-skills
python scripts/skill.py info <skill_name>
python scripts/skill.py remove <skill_name>
python scripts/skill.py update <skill_file>
```

## 快速开始

```bash
# 列出已安装的 Skill
python scripts/skill.py list-skills

# 安装新的 Skill
python scripts/skill.py install pdf-to-can-csv.skill

# 查看 Skill 详细信息
python scripts/skill.py info pdf-to-can-csv

# 更新 Skill
python scripts/skill.py update pdf-to-can-csv.skill

# 删除 Skill
python scripts/skill.py remove pdf-to-can-csv
```
