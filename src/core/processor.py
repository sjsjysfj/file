import os
from PIL import Image, ImageOps
from src.utils.logger import logger

class ImageProcessor:
    @staticmethod
    def split_image(image_path, output_dir, output_format=None, quality=95, rows=2, cols=2):
        """
        Splits an image into rows * cols equal parts.
        """
        try:
            img = Image.open(image_path)
            # Preserve metadata
            exif = img.info.get('exif')
            
            width, height = img.size
            
            # Calculate grid sizes
            part_width = width // cols
            part_height = height // rows

            # Define regions
            regions = []
            for r in range(rows):
                for c in range(cols):
                    left = c * part_width
                    top = r * part_height
                    # For the last column/row, take the remaining pixels to handle rounding
                    right = width if c == cols - 1 else (c + 1) * part_width
                    bottom = height if r == rows - 1 else (r + 1) * part_height
                    regions.append((left, top, right, bottom))
            
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            ext = output_format if output_format else os.path.splitext(image_path)[1][1:]
            if not ext:
                ext = "jpg"
            
            output_files = []
            
            for i, box in enumerate(regions):
                cropped = img.crop(box)
                output_filename = f"{base_name}_{i+1}.{ext}"
                output_path = os.path.join(output_dir, output_filename)
                
                save_kwargs = {'quality': quality}
                if exif:
                    save_kwargs['exif'] = exif
                
                # Handle RGBA to RGB conversion for JPEG
                if ext.lower() in ['jpg', 'jpeg'] and cropped.mode == 'RGBA':
                    cropped = cropped.convert('RGB')
                    
                cropped.save(output_path, **save_kwargs)
                output_files.append(output_path)
                
            logger.info(f"Successfully split image: {image_path} into {rows}x{cols}")
            return output_files

        except Exception as e:
            logger.error(f"Error splitting image {image_path}: {e}")
            raise

    @staticmethod
    def stitch_images(image_paths, output_path, mode='resize', output_format=None, quality=95):
        """
        Stitches multiple images vertically.
        mode: 'resize' (scale to max width), 'crop' (crop to min width), 'fill' (pad to max width)
        """
        try:
            final_img = ImageProcessor._stitch_logic(image_paths, mode)
            
            # Save
            # If output_path doesn't have an extension, we need to add one.
            # We also need to know the extension to handle RGBA->RGB conversion for JPEG.
            
            # 1. Determine extension
            ext = os.path.splitext(output_path)[1][1:] # Get existing extension if any
            
            if output_format:
                # User specified format overrides everything
                target_ext = output_format
            elif ext:
                # Use existing extension from path
                target_ext = ext
            else:
                # Default to jpg
                target_ext = "jpg"

            # 2. Ensure output_path has correct extension
            if not ext or (output_format and ext.lower() != output_format.lower()):
                # If no extension or user forced a different format, append/replace it
                base = os.path.splitext(output_path)[0]
                output_path = f"{base}.{target_ext}"
            
            save_kwargs = {'quality': quality}
            # Use EXIF from first image if available
            try:
                with Image.open(image_paths[0]) as first_img:
                    exif = first_img.info.get('exif')
                    if exif:
                        save_kwargs['exif'] = exif
            except:
                pass

            if target_ext.lower() in ['jpg', 'jpeg'] and final_img.mode == 'RGBA':
                final_img = final_img.convert('RGB')

            final_img.save(output_path, **save_kwargs)
            logger.info(f"Successfully stitched {len(image_paths)} images to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error stitching images: {e}")
            raise

    @staticmethod
    def generate_stitch_preview(image_paths, mode='resize', max_width=300):
        """
        Generates a low-resolution preview of the stitched image.
        Returns a PIL Image object.
        """
        try:
            # Create a simplified list of images (downscaled)
            preview_images = []
            for p in image_paths:
                try:
                    img = Image.open(p)
                    # Downscale while preserving aspect ratio
                    img.thumbnail((max_width, max_width))
                    preview_images.append(img)
                except Exception as e:
                    logger.warning(f"Could not load {p} for preview: {e}")
            
            if not preview_images:
                return None
                
            # Use the same stitching logic but with in-memory images
            return ImageProcessor._stitch_in_memory(preview_images, mode)
        except Exception as e:
            logger.error(f"Error generating preview: {e}")
            return None

    @staticmethod
    def _stitch_logic(image_paths, mode):
        images = [Image.open(p) for p in image_paths]
        if not images:
            raise ValueError("No images provided for stitching")
        return ImageProcessor._stitch_in_memory(images, mode)

    @staticmethod
    def _stitch_in_memory(images, mode):
        widths, heights = zip(*(i.size for i in images))
        
        if mode == 'crop':
            target_width = min(widths)
        else: # resize or fill
            target_width = max(widths)

        processed_images = []
        for img in images:
            if img.size[0] == target_width:
                processed_images.append(img)
                continue

            if mode == 'resize':
                # Calculate new height to maintain aspect ratio
                aspect_ratio = img.size[1] / img.size[0]
                new_height = int(target_width * aspect_ratio)
                processed_images.append(img.resize((target_width, new_height), Image.Resampling.LANCZOS))
            elif mode == 'crop':
                # Center crop
                left = (img.size[0] - target_width) // 2
                processed_images.append(img.crop((left, 0, left + target_width, img.size[1])))
            elif mode == 'fill':
                # Pad with white (or transparent if RGBA)
                new_img = Image.new(img.mode, (target_width, img.size[1]), (255, 255, 255, 0))
                left = (target_width - img.size[0]) // 2
                new_img.paste(img, (left, 0))
                processed_images.append(new_img)

        total_height = sum(img.size[1] for img in processed_images)
        
        # Determine mode for final image
        final_mode = 'RGB'
        if any(img.mode == 'RGBA' for img in processed_images):
            final_mode = 'RGBA'
        
        final_img = Image.new(final_mode, (target_width, total_height))
        
        y_offset = 0
        for img in processed_images:
            final_img.paste(img, (0, y_offset))
            y_offset += img.size[1]
            
        return final_img
