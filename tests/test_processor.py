import os
import pytest
from PIL import Image
from src.core.processor import ImageProcessor

@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path

@pytest.fixture
def sample_image(temp_dir):
    img = Image.new('RGB', (100, 100), color='red')
    path = os.path.join(temp_dir, "test_img.jpg")
    img.save(path)
    return path

@pytest.fixture
def sample_images_stitch(temp_dir):
    img1 = Image.new('RGB', (100, 100), color='red')
    path1 = os.path.join(temp_dir, "stitch1.jpg")
    img1.save(path1)
    
    img2 = Image.new('RGB', (50, 50), color='blue')
    path2 = os.path.join(temp_dir, "stitch2.jpg")
    img2.save(path2)
    
    return [path1, path2]

def test_split_image(sample_image, temp_dir):
    # Default 2x2
    output_files = ImageProcessor.split_image(sample_image, str(temp_dir))
    assert len(output_files) == 4
    
    for f in output_files:
        assert os.path.exists(f)
        with Image.open(f) as img:
            assert img.size == (50, 50)

def test_split_image_grid(sample_image, temp_dir):
    # 100x100 image, Split 2 rows x 5 cols -> 20 width, 50 height
    output_files = ImageProcessor.split_image(sample_image, str(temp_dir), rows=2, cols=5)
    assert len(output_files) == 10
    
    for f in output_files:
        assert os.path.exists(f)
        with Image.open(f) as img:
            assert img.size == (20, 50)

def test_stitch_images_resize(sample_images_stitch, temp_dir):
    output_path = os.path.join(temp_dir, "stitched.jpg")
    result = ImageProcessor.stitch_images(sample_images_stitch, output_path, mode='resize')
    
    assert os.path.exists(result)
    with Image.open(result) as img:
        # Width should be max (100)
        assert img.width == 100
        # Height: 
        # img1 (100x100) -> 100x100
        # img2 (50x50) -> scaled to 100 width -> 100x100
        # Total height = 200
        assert img.height == 200

def test_stitch_images_crop(sample_images_stitch, temp_dir):
    output_path = os.path.join(temp_dir, "stitched_crop.jpg")
    result = ImageProcessor.stitch_images(sample_images_stitch, output_path, mode='crop')
    
    with Image.open(result) as img:
        # Width should be min (50)
        assert img.width == 50
        # Height:
        # img1 (100x100) -> crop to 50x100
        # img2 (50x50) -> 50x50
        # Total height = 150
        assert img.height == 150

def test_stitch_images_fill(sample_images_stitch, temp_dir):
    output_path = os.path.join(temp_dir, "stitched_fill.jpg")
    result = ImageProcessor.stitch_images(sample_images_stitch, output_path, mode='fill')
    
    with Image.open(result) as img:
        # Width should be max (100)
        assert img.width == 100
        # Height:
        # img1 (100x100) -> 100x100
        # img2 (50x50) -> padded to 100x50
        # Total height = 150
        assert img.height == 150
