from PIL import Image, ImageEnhance
import io

def preprocess_image(image_path: str) -> bytes:
    with Image.open(image_path) as img:
        # Auto-rotate based on EXIF
        try:
            from PIL import ImageOps
            img = ImageOps.exif_transpose(img)
        except Exception:
            pass
            
        # Downscale to ~1600px long side
        max_size = 1600
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            
        # Mild contrast enhancement
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)
        
        # Convert to bytes
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=85)
        return output.getvalue()
