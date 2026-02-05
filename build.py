import subprocess
import shutil
import os
import zipfile

def build():
    print("Starting build...")
    
    # PyInstaller arguments
    cmd = [
        'pyinstaller',
        'src/main.py',
        '--name=ImageExpert',
        '--onefile',
        '--windowed',
        '--noconfirm',
        '--add-data=src;src',
    ]
    
    try:
        subprocess.check_call(cmd, shell=True)
        print("Build complete.")
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        return

    # Post-build: Create release folder
    if os.path.exists('release'):
        shutil.rmtree('release')
    os.makedirs('release')
    
    exe_path = os.path.join('dist', 'ImageExpert.exe')
    if os.path.exists(exe_path):
        shutil.copy(exe_path, 'release')
        print(f"Copied {exe_path} to release/")
    else:
        print("Error: Executable not found!")
        return

    # Create Zip
    zip_name = 'release/ImageExpert_v1.0.zip'
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(os.path.join('release', 'ImageExpert.exe'), 'ImageExpert.exe')
    
    print(f"Created zip archive: {zip_name}")

if __name__ == "__main__":
    build()
