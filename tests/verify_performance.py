import sys
import os
import time
import shutil
from PyQt6.QtWidgets import QApplication
from src.ui.widgets import ImageListWidget
from PIL import Image

def test_performance():
    app = QApplication(sys.argv)
    
    # Setup 1000 images
    test_dir = "perf_test_images"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    # Create a reasonably sized image
    base_img = Image.new('RGB', (500, 500), color='blue')
    base_path = os.path.join(test_dir, "base.jpg")
    base_img.save(base_path)
    
    print("Generating 1000 images...")
    files = []
    for i in range(1000):
        p = os.path.join(test_dir, f"img_{i}.jpg")
        shutil.copy(base_path, p)
        files.append(p)
        
    widget = ImageListWidget()
    # Don't show, just measure addition time
    
    print("Adding 1000 images to widget...")
    start_time = time.time()
    
    for f in files:
        widget.add_image(f)
        
    end_time = time.time()
    duration = (end_time - start_time) * 1000
    print(f"Time to add 1000 items: {duration:.2f} ms")
    
    with open("perf_result.txt", "w") as f:
        f.write(f"Time: {duration:.2f} ms\n")
        if duration < 300:
            f.write("PASS")
        else:
            f.write("FAIL")

    if duration < 300:
        print("PASS: UI response time < 300ms")
    else:
        print("FAIL: UI response time > 300ms")
        
    # Clean up
    # Wait a bit to avoid immediate errors in thread
    time.sleep(1)
    shutil.rmtree(test_dir)

if __name__ == "__main__":
    test_performance()
