import os
import subprocess
import sys

def build_exe():
    """打包应用程序为exe文件"""
    # 确保在项目根目录
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    # 构建命令
    cmd = [
        "pyinstaller",
        "--name=JiDiHelper",  # 应用程序名称
        "--windowed",  # 不显示控制台窗口
        "--onefile",  # 打包成单个exe文件
        "--add-data=src;src",  # 添加src目录
        "--manifest=admin.manifest",  # 添加管理员权限manifest
        "--icon=1.ico",  # 添加应用程序图标
        "--clean",  # 清理临时文件
        "--noconfirm",  # 不确认覆盖
        "main.py"  # 主程序入口
    ]
    
    # 执行打包命令
    try:
        subprocess.run(cmd, check=True)
        print("打包成功！exe文件位于 dist 目录中。")
    except subprocess.CalledProcessError as e:
        print(f"打包失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()