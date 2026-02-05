import os
import subprocess
import sys

def build():
    # Install pyinstaller if not present
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Define PyInstaller command
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name", "ImageProcessorPro",
        "--add-data", f"src{os.pathsep}src",  # Include src package
        "run.py"
    ]
    
    print(f"Running build command: {' '.join(cmd)}")
    subprocess.check_call(cmd)
    
    print("\nBuild completed successfully!")
    print(f"Executable is located in: {os.path.join(os.getcwd(), 'dist', 'ImageProcessorPro', 'ImageProcessorPro.exe')}")

if __name__ == "__main__":
    build()
