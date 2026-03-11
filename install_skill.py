#!/usr/bin/env python3
"""
安装Skill文件的脚本
用法: python install_skill.py <skill_file_path>

功能:
1. 解压.skill文件(7z格式)到临时目录
2. 将解压内容移动到.github/skills/目录下
3. 如果目标目录不存在则创建
4. 如果skill文件夹已存在，提示是否替换
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def extract_skill_file(skill_file_path: str, temp_dir: str) -> str:
    """
    使用7z解压skill文件
    
    参数:
        skill_file_path: skill文件的路径
        temp_dir: 临时目录
        
    返回:
        解压后文件夹的路径
    """
    skill_file = Path(skill_file_path)
    
    if not skill_file.exists():
        raise FileNotFoundError(f"Skill文件不存在: {skill_file_path}")
    
    if skill_file.suffix.lower() != '.skill':
        raise ValueError(f"文件类型错误，应为.skill文件: {skill_file_path}")
    
    print(f"📦 正在解压: {skill_file.name}")
    
    # 使用py7zr库解压
    try:
        import py7zr
        with py7zr.SevenZipFile(skill_file, 'r') as archive:
            archive.extractall(path=temp_dir)
        print(f"✅ 解压成功")
    except ImportError:
        # 如果没有py7zr，尝试使用7z命令行工具
        print("py7zr未安装，尝试使用7z命令行工具...")
        try:
            result = subprocess.run(
                ['7z', 'x', str(skill_file), f'-o{temp_dir}'],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✅ 解压成功")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"7z解压失败: {e.stderr}") from e
    except (OSError, RuntimeError) as e:
        raise RuntimeError(f"解压失败: {e}") from e
    
    # 查找解压后的文件夹（通常skill文件夹名称与skill文件名相同，去掉.skill后缀）
    skill_name = skill_file.stem  # 去掉.skill后缀
    extracted_items = list(Path(temp_dir).iterdir())
    
    if len(extracted_items) == 1 and extracted_items[0].is_dir():
        # 如果只有一个文件夹，使用该文件夹
        skill_folder = extracted_items[0]
    elif any(item.name == skill_name for item in extracted_items if item.is_dir()):
        # 如果有与skill名称相同的文件夹，使用该文件夹
        skill_folder = Path(temp_dir) / skill_name
    else:
        # 否则查找第一个文件夹
        folders = [item for item in extracted_items if item.is_dir()]
        if folders:
            skill_folder = folders[0]
        else:
            raise ValueError(f"解压后未找到skill文件夹")
    
    return str(skill_folder)


def get_skill_name(skill_folder_path: str) -> str:
    """
    从skill文件夹获取skill名称
    
    参数:
        skill_folder_path: skill文件夹的路径
        
    返回:
        skill名称
    """
    return Path(skill_folder_path).name


def get_target_skills_dir(base_dir: str = ".") -> Path:
    """
    获取或创建.github/skills目录
    
    参数:
        base_dir: 基础目录（默认为当前目录）
        
    返回:
        .github/skills目录的Path对象
    """
    github_dir = Path(base_dir) / ".github"
    skills_dir = github_dir / "skills"
    
    # 创建目录（如果不存在）
    skills_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 目标目录: {skills_dir.absolute()}")
    
    return skills_dir


def prompt_overwrite(skill_name: str) -> bool:
    """
    提示用户是否覆盖已存在的skill
    
    参数:
        skill_name: skill名称
        
    返回:
        True表示覆盖，False表示不覆盖
    """
    while True:
        response = input(f"\n⚠️  Skill '{skill_name}' 已存在。是否替换/升级？(y/n): ").lower().strip()
        if response in ('y', 'yes', '是'):
            return True
        elif response in ('n', 'no', '否'):
            return False
        else:
            print("请输入 y/n")


def install_skill(skill_file_path: str, base_dir: str = ".") -> bool:
    """
    安装skill文件
    
    参数:
        skill_file_path: skill文件的路径
        base_dir: 基础目录
        
    返回:
        True表示安装成功，False表示被用户取消
    """
    try:
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:  # pylint: disable=broad-except
            print(f"\n🔧 开始安装Skill文件...")
            print(f"📍 临时目录: {temp_dir}")
            
            # 解压skill文件
            extracted_folder = extract_skill_file(skill_file_path, temp_dir)
            skill_name = get_skill_name(extracted_folder)
            print(f"📌 Skill名称: {skill_name}")
            
            # 获取目标目录
            skills_dir = get_target_skills_dir(base_dir)
            target_folder = skills_dir / skill_name
            
            # 检查目标文件夹是否已存在
            if target_folder.exists():
                print(f"📂 已找到现有Skill: {target_folder}")
                if not prompt_overwrite(skill_name):
                    print("❌ 取消安装")
                    return False
                print(f"🗑️  移除旧版本...")
                shutil.rmtree(target_folder)
            
            # 复制到目标目录
            print(f"📋 复制到目标位置...")
            shutil.copytree(extracted_folder, target_folder)
            print(f"✅ Skill安装成功！")
            print(f"📍 安装位置: {target_folder.absolute()}")
            
            return True
            
    except (FileNotFoundError, ValueError, RuntimeError, shutil.Error) as e:
        print(f"❌ 安装失败: {e}")
        return False


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python install_skill.py <skill_file_path>")
        print("\n示例:")
        print("  python install_skill.py pdf-to-can-csv.skill")
        print("  python install_skill.py ./my-skill.skill")
        sys.exit(1)
    
    skill_file = sys.argv[1]
    
    # 如果提供了基础目录作为第二个参数
    base_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    
    success = install_skill(skill_file, base_dir)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
