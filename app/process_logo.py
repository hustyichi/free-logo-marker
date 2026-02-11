import os
import io
from PIL import Image, ImageOps
from rembg import remove
from pathlib import Path

def process_logo(input_path: str, output_dir: str):
    """
    Removes background, crops to content, adds padding, and saves as PNG and ICO.

    Args:
        input_path: Path to the input image.
        output_dir: Directory to save processed images (output files will be logo.png and favicon.ico).

    Returns:
        Tuple containing paths to the generated PNG and ICO files.
    """
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    print(f"Processing {input_path}...")

    # 1. Read Image
    with open(input_path, 'rb') as i:
        input_data = i.read()

    # 2. Remove Background (rembg)
    print("Removing background (this may download models on first run)...")
    try:
        subject_data = remove(input_data)
    except Exception as e:
        print(f"Error removing background: {e}")
        raise

    # 3. Post-process with PIL
    img = Image.open(io.BytesIO(subject_data))

    # 4. Crop to content (getbbox)
    # The image is now RGBA. We need to find the bounding box of non-transparent pixels.
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
        print(f"Cropped to bounding box: {bbox}")
    else:
        print("Warning: No content found in image (all transparent?)")

    # 5. Resize to 512x512 with safe area
    final_size = (512, 512)
    safe_area_pct = 0.05
    # Calculate target size for the content: 512 * (1 - 0.05*2) = 512 * 0.9 = ~460
    target_content_size = int(512 * (1 - safe_area_pct * 2))

    # Maintain aspect ratio while fitting within target_content_size
    img.thumbnail((target_content_size, target_content_size), Image.Resampling.LANCZOS)

    # Create new transparent canvas
    new_img = Image.new("RGBA", final_size, (0, 0, 0, 0))

    # Paste centered
    # Calculate offset to center the thumbnail in the 512x512 canvas
    offset = ((final_size[0] - img.size[0]) // 2, (final_size[1] - img.size[1]) // 2)
    new_img.paste(img, offset)

    # 6. Save PNG
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    png_path = output_dir / "logo.png"
    new_img.save(png_path, format="PNG")
    print(f"Saved PNG: {png_path}")

    # 7. Save ICO
    ico_path = output_dir / "favicon.ico"
    # Sizes: 16, 32, 48, 64
    # ICO format supports multiple sizes in one file
    try:
        new_img.save(ico_path, format="ICO", sizes=[(16,16), (32,32), (48,48), (64,64)])
        print(f"Saved ICO: {ico_path}")
    except Exception as e:
        print(f"Error saving ICO: {e}")
        # Non-critical, but good to report

    return png_path, ico_path
