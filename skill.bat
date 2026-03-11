@echo off
REM Skill 管理工具命令行入口（Windows批处理）
REM 用法: skill.bat install pdf-to-can-csv.skill
REM      skill.bat list-skills
REM      skill.bat info pdf-to-can-csv

python "%~dp0skill.py" %*
