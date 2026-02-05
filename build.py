import PyInstaller.__main__
import shutil
import os
import zipfile

def build():
    print("Starting build...")
    
    # PyInstaller arguments
    args = [
        'src/main.py',
        '--name=ImageExpert',
        '--onefile',
        '--windowed',
        '--noconfirm',
        '--add-data=src;src',  # PyInstaller handles this separator correctly when passed as list
    ]
    
    PyInstaller.__main__.run(args)
    print("Build complete.")

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
