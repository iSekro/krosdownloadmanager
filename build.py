"""
Build script for creating KrosDownloadManager portable .exe for Windows.

Usage:
    python build.py

Requirements:
    pip install pyinstaller

This creates a single portable .exe file in the dist/ directory.
"""

import os
import subprocess
import sys


def build():
    """Build the portable executable."""
    root_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(root_dir, "src")

    main_script = os.path.join(src_dir, "krosdownloadmanager", "main.py")

    if not os.path.exists(main_script):
        print(f"ERROR: Main script not found: {main_script}")
        sys.exit(1)

    icon_path = os.path.join(src_dir, "krosdownloadmanager", "assets", "icon.ico")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "KrosDownloadManager",
        "--add-data", f"{src_dir}/krosdownloadmanager/assets{os.pathsep}krosdownloadmanager/assets",
        "--hidden-import", "customtkinter",
        "--hidden-import", "requests",
        "--hidden-import", "PIL",
        "--hidden-import", "pyperclip",
        "--collect-all", "customtkinter",
    ]

    if os.path.exists(icon_path):
        cmd.extend(["--icon", icon_path])

    cmd.append(main_script)

    print("=" * 60)
    print("  Building KrosDownloadManager Portable .exe")
    print("=" * 60)
    print(f"\nCommand: {' '.join(cmd)}\n")

    result = subprocess.run(cmd, cwd=root_dir)

    if result.returncode == 0:
        exe_path = os.path.join(root_dir, "dist", "KrosDownloadManager.exe")
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"\n{'=' * 60}")
            print(f"  BUILD SUCCESSFUL!")
            print(f"  Output: {exe_path}")
            print(f"  Size:   {size_mb:.1f} MB")
            print(f"{'=' * 60}")
        else:
            print("\nBuild completed but .exe not found at expected path.")
            print("Check the dist/ directory.")
    else:
        print(f"\nBuild FAILED with exit code {result.returncode}")
        sys.exit(1)


if __name__ == "__main__":
    build()
