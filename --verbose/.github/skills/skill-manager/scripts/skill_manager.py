#!/usr/bin/env python3
"""
Skill 文件管理工具 - 使用 Typer 创建的 CLI 应用

功能:
1. install: 安装 Skill 文件
2. list: 列出已安装的 Skill
3. remove: 移除已安装的 Skill
4. update: 更新 Skill 文件
"""

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

import typer

app = typer.Typer(help="🛠️  Skill 文件管理工具", pretty_exceptions_enable=False)


# ============================================================================
# 工具函数
# ============================================================================


def extract_skill_file(skill_file_path: str, temp_dir: str, verbose: bool = False) -> str:
    """
    使用7z解压skill文件

    参数:
        skill_file_path: skill文件的路径
        temp_dir: 临时目录
        verbose: 是否输出详细信息

    返回:
        解压后文件夹的路径
    """
    skill_file = Path(skill_file_path)

    if not skill_file.exists():
        raise FileNotFoundError(f"Skill文件不存在: {skill_file_path}")

    if skill_file.suffix.lower() != ".skill":
        raise ValueError(f"文件类型错误，应为.skill文件: {skill_file_path}")

    typer.echo(f"📦 正在解压: {skill_file.name}")

    # 使用py7zr库解压
    try:
        import py7zr

        with py7zr.SevenZipFile(skill_file, "r") as archive:
            archive.extractall(path=temp_dir)
        typer.echo("✅ 解压成功")
    except ImportError:
        # 如果没有py7zr，尝试使用7z命令行工具
        if verbose:
            typer.echo("py7zr未安装，尝试使用7z命令行工具...")
        try:
            result = subprocess.run(
                ["7z", "x", str(skill_file), f"-o{temp_dir}"],
                capture_output=True,
                text=True,
                check=True,
            )
            typer.echo("✅ 解压成功")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"7z解压失败: {e.stderr}") from e
    except (OSError, RuntimeError) as e:
        raise RuntimeError(f"解压失败: {e}") from e

    # 查找解压后的文件夹
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
            raise ValueError("解压后未找到skill文件夹")

    return str(skill_folder)


def get_skill_name(skill_folder_path: str) -> str:
    """获取skill文件夹的名称"""
    return Path(skill_folder_path).name


def get_target_skills_dir(base_dir: str = ".") -> Path:
    """获取或创建.github/skills目录"""
    github_dir = Path(base_dir) / ".github"
    skills_dir = github_dir / "skills"

    # 创建目录（如果不存在）
    skills_dir.mkdir(parents=True, exist_ok=True)
    return skills_dir


def list_installed_skills(base_dir: str = ".") -> list[Path]:
    """列出所有已安装的skill"""
    skills_dir = get_target_skills_dir(base_dir)
    if not skills_dir.exists():
        return []
    return sorted([item for item in skills_dir.iterdir() if item.is_dir()])


def skill_exists(skill_name: str, base_dir: str = ".") -> bool:
    """检查skill是否已存在"""
    skills_dir = get_target_skills_dir(base_dir)
    return (skills_dir / skill_name).exists()


# ============================================================================
# CLI 命令
# ============================================================================


@app.command()
def install(
    skill_file: str = typer.Argument(..., help="Skill 文件路径"),
    base_dir: str = typer.Option(
        ".", "--base-dir", "-b", help="基础目录（默认为当前目录）"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="强制覆盖，跳过确认"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="详细输出"),
) -> None:
    """
    📦 安装 Skill 文件

    示例:
        skill-manager install pdf-to-can-csv.skill
        skill-manager install ./my-skill.skill --force
    """
    try:
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            if verbose:
                typer.echo(f"🔧 开始安装Skill文件...")
                typer.echo(f"📍 临时目录: {temp_dir}")

            # 解压skill文件
            extracted_folder = extract_skill_file(skill_file, temp_dir, verbose)
            skill_name = get_skill_name(extracted_folder)

            if verbose:
                typer.echo(f"📌 Skill名称: {skill_name}")

            # 获取目标目录
            skills_dir = get_target_skills_dir(base_dir)
            target_folder = skills_dir / skill_name

            if verbose:
                typer.echo(f"📁 目标目录: {skills_dir.absolute()}")

            # 检查目标文件夹是否已存在
            if target_folder.exists():
                typer.echo(f"📂 已找到现有Skill: {target_folder.relative_to(base_dir)}")

                if not force:
                    if not typer.confirm(
                        f"是否替换/升级 '{skill_name}'?", default=False
                    ):
                        typer.echo("❌ 取消安装")
                        raise typer.Exit(code=1)

                if verbose:
                    typer.echo("🗑️  移除旧版本...")
                shutil.rmtree(target_folder)

            # 复制到目标目录
            if verbose:
                typer.echo("📋 复制到目标位置...")

            shutil.copytree(extracted_folder, target_folder)
            typer.secho("✅ Skill 安装成功！", fg=typer.colors.GREEN, bold=True)
            typer.echo(f"📍 安装位置: {target_folder.absolute()}")

    except (FileNotFoundError, ValueError, RuntimeError, shutil.Error) as e:
        typer.secho(f"❌ 安装失败: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command()
def list_skills(
    base_dir: str = typer.Option(
        ".", "--base-dir", "-b", help="基础目录（默认为当前目录）"
    ),
) -> None:
    """
    📋 列出已安装的 Skill

    示例:
        skill-manager list
        skill-manager list --base-dir ./project
    """
    skills = list_installed_skills(base_dir)

    if not skills:
        typer.echo("📭 未找到已安装的 Skill")
        return

    typer.echo(f"\n📦 已安装的 Skill ({len(skills)}):\n")
    for idx, skill_path in enumerate(skills, 1):
        skill_info_file = skill_path / "SKILL.md"
        has_info = "✓" if skill_info_file.exists() else "✗"

        typer.echo(f"  {idx}. {skill_path.name:30} [{has_info}]")

    typer.echo()


@app.command()
def remove(
    skill_name: str = typer.Argument(..., help="要删除的 Skill 名称"),
    base_dir: str = typer.Option(
        ".", "--base-dir", "-b", help="基础目录（默认为当前目录）"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="强制删除，跳过确认"),
) -> None:
    """
    🗑️  删除已安装的 Skill

    示例:
        skill-manager remove pdf-to-can-csv
        skill-manager remove my-skill --force
    """
    try:
        skills_dir = get_target_skills_dir(base_dir)
        target_folder = skills_dir / skill_name

        if not target_folder.exists():
            typer.secho(
                f"❌ Skill '{skill_name}' 不存在", fg=typer.colors.RED
            )
            raise typer.Exit(code=1)

        if not force:
            if not typer.confirm(
                f"确定要删除 '{skill_name}'?", default=False
            ):
                typer.echo("❌ 取消删除")
                raise typer.Exit(code=1)

        shutil.rmtree(target_folder)
        typer.secho(
            f"✅ Skill '{skill_name}' 已删除", fg=typer.colors.GREEN, bold=True
        )

    except (FileNotFoundError, shutil.Error) as e:
        typer.secho(f"❌ 删除失败: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command()
def update(
    skill_file: str = typer.Argument(..., help="新的 Skill 文件路径"),
    base_dir: str = typer.Option(
        ".", "--base-dir", "-b", help="基础目录（默认为当前目录）"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="详细输出"),
) -> None:
    """
    🔄 更新已安装的 Skill（等同于 install --force）

    示例:
        skill-manager update pdf-to-can-csv.skill
    """
    # 调用 install 命令，使用 --force 标志
    install(
        skill_file=skill_file,
        base_dir=base_dir,
        force=True,
        verbose=verbose,
    )


@app.command()
def info(
    skill_name: str = typer.Argument(..., help="Skill 名称"),
    base_dir: str = typer.Option(
        ".", "--base-dir", "-b", help="基础目录（默认为当前目录）"
    ),
) -> None:
    """
    ℹ️  显示 Skill 的详细信息

    示例:
        skill-manager info pdf-to-can-csv
    """
    try:
        skills_dir = get_target_skills_dir(base_dir)
        skill_folder = skills_dir / skill_name

        if not skill_folder.exists():
            typer.secho(f"❌ Skill '{skill_name}' 不存在", fg=typer.colors.RED)
            raise typer.Exit(code=1)

        typer.echo(f"\n📦 Skill 信息: {skill_name}\n")
        typer.echo(f"位置: {skill_folder.absolute()}")

        # 列出skill文件夹的内容
        items = list(skill_folder.rglob("*"))
        files = [item for item in items if item.is_file()]

        typer.echo(f"文件数: {len(files)}")
        typer.echo("\n📄 包含的文件:")

        for file_path in sorted(files):
            relative = file_path.relative_to(skill_folder)
            typer.echo(f"  - {relative}")

        typer.echo()

    except (FileNotFoundError, OSError) as e:
        typer.secho(f"❌ 查询失败: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.callback()
def callback(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", help="显示版本信息"
    )
) -> None:
    """🛠️  Skill 文件管理工具"""
    if version:
        typer.echo("Skill Manager v1.0.0")
        raise typer.Exit()


def main() -> None:
    """主函数"""
    app()


if __name__ == "__main__":
    main()
