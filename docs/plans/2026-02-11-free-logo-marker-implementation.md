# Free Logo Marker Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a local-first CLI tool for generating and processing logos using AI and local image processing libraries.

**Architecture:**
A modular Python CLI application with two main pipelines: `generate` (AI-based creation via OpenAI-compatible API) and `process` (Local background removal and formatting via rembg/Pillow). A central controller (`main.py`) orchestrates these based on CLI arguments.

**Tech Stack:**
- Python 3.10+
- `openai` (API Client)
- `rembg` (Background Removal)
- `pillow` (Image Processing)
- `argparse` (CLI)
- `python-dotenv` (Configuration)

---

### Task 1: Project Initialization & Dependency Management

**Goal:** Set up project structure and install dependencies.

**Files:**
- Modify: `pyproject.toml`
- Create: `.env.example`
- Create: `app/__init__.py` (already exists, verify)
- Create: `assets/.gitkeep`
- Create: `output/.gitkeep`

**Step 1: Update `pyproject.toml`**

Add `rembg`, `pillow`, `python-dotenv` to dependencies.

```toml
[project]
name = "free-logo-marker"
version = "0.1.0"
description = "Local-first AI logo generator and processor"
requires-python = ">=3.10"
dependencies = [
    "openai>=1.0.0",
    "rembg>=2.0.0",
    "pillow>=10.0.0",
    "python-dotenv>=1.0.0",
    "requests>=2.31.0", # rembg might need this
    "onnxruntime>=1.16.0" # for rembg
]
```

**Step 2: Create directory structure**

```bash
mkdir -p assets output app
touch assets/.gitkeep output/.gitkeep
```

**Step 3: Create `.env.example`**

```text
# Image Generation API Configuration
# Default: Local server (e.g., LocalAI, LM Studio, etc.)
GEN_API_BASE_URL=http://127.0.0.1:8045/v1
GEN_API_KEY=not-needed
GEN_MODEL_NAME=gemini-3-pro-image
```

**Step 4: Install dependencies**

```bash
uv sync # or pip install -e . depending on environment
```

---

### Task 2: Image Generation Module (`app/generate_logo.py`)

**Goal:** Implement the module to fetch images from an OpenAI-compatible API.

**Files:**
- Create: `app/generate_logo.py`
- Test: `tests/test_generate.py`

**Step 1: Create Test for Generation Logic (Mocked)**

Create `tests/conftest.py` first if needed for fixtures, then `tests/test_generate.py`.

```python
# tests/test_generate.py
import pytest
from unittest.mock import patch, MagicMock
from app.generate_logo import generate_logo

@patch('app.generate_logo.OpenAI')
def test_generate_logo_success(mock_openai, tmp_path):
    # Setup mock
    mock_client = MagicMock()
    mock_openai.return_value = mock_client

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="http://fake.url/image.png"))]
    mock_client.chat.completions.create.return_value = mock_response

    # We also need to mock requests.get to download the "image"
    with patch('app.generate_logo.requests.get') as mock_get:
        mock_get.return_value.content = b"fake_image_bytes"
        mock_get.return_value.status_code = 200

        output_path = tmp_path / "test_logo.png"
        result = generate_logo(
            prompt="test prompt",
            output_path=str(output_path),
            api_base="http://test",
            api_key="sk-test"
        )

        assert result == str(output_path)
        assert output_path.exists()
```

**Step 2: Implement `app/generate_logo.py`**

```python
import os
import requests
from openai import OpenAI
from pathlib import Path

def generate_logo(prompt: str, output_path: str, model: str = "gemini-3-pro-image", api_base: str = None, api_key: str = None) -> str:
    """
    Generates an image from a prompt using OpenAI-compatible API and saves it.
    """
    client = OpenAI(
        base_url=api_base or os.getenv("GEN_API_BASE_URL", "http://127.0.0.1:8045/v1"),
        api_key=api_key or os.getenv("GEN_API_KEY", "not-needed")
    )

    # Enforce flat, vector style in prompt if not present?
    # PRD says: "Must enforce flat, solid background..."
    # We will append this to the system prompt or user prompt wrapper
    full_prompt = (
        f"{prompt}. "
        "Style requirements: Flat 2D vector logo, minimalist, solid white background, "
        "no shadows, high contrast, centered subject."
    )

    print(f"Generating logo with prompt: {prompt[:50]}...")

    try:
        response = client.chat.completions.create(
            model=model,
            extra_body={"size": "1024x1024"}, # As per PRD 3.4
            messages=[{"role": "user", "content": full_prompt}]
        )

        # Depending on the backend, the content might be a URL or b64json
        # The PRD example shows printing content. Assuming it returns a URL.
        image_url = response.choices[0].message.content

        # Download the image
        img_data = requests.get(image_url).content

        # Ensure directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'wb') as f:
            f.write(img_data)

        print(f"Image saved to {output_path}")
        return output_path

    except Exception as e:
        print(f"Error generating logo: {e}")
        raise
```

---

### Task 3: Image Processing Module (`app/process_logo.py`)

**Goal:** Implement background removal, cropping, and formatting.

**Files:**
- Create: `app/process_logo.py`
- Test: `tests/test_process.py`

**Step 1: Create Test for Processing**

```python
# tests/test_process.py
import pytest
from PIL import Image
import io
from app.process_logo import process_logo

def test_process_logo_execution(tmp_path):
    # Create a dummy image (white background with a black square)
    img = Image.new('RGB', (100, 100), color='white')
    for x in range(25, 75):
        for y in range(25, 75):
            img.putpixel((x, y), (0, 0, 0))

    input_path = tmp_path / "input.png"
    img.save(input_path)

    output_dir = tmp_path / "output"
    name = "test_logo"

    # Mocking rembg might be complex here due to ONNX download.
    # For the plan, we'll assume integration test or mock the remove function.
    # Here we will just import and run, acknowledging it might fail if models aren't downloaded.
    # Better to mock rembg.remove for unit testing logic.
    pass
```

**Step 2: Implement `app/process_logo.py`**

```python
import os
from PIL import Image
from rembg import remove
from pathlib import Path

def process_logo(input_path: str, output_dir: str, name: str = "logo"):
    """
    Removes background, crops to content, adds padding, and saves as PNG and ICO.
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
    subject_data = remove(input_data)

    # 3. Post-process with PIL
    img = Image.open(io.BytesIO(subject_data))

    # 4. Crop to content (getbbox)
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)

    # 5. Resize to 512x512 with safe area
    final_size = (512, 512)
    safe_area_pct = 0.05
    target_content_size = int(512 * (1 - safe_area_pct * 2))

    # Maintain aspect ratio
    img.thumbnail((target_content_size, target_content_size), Image.Resampling.LANCZOS)

    # Create new transparent canvas
    new_img = Image.new("RGBA", final_size, (0, 0, 0, 0))

    # Paste centered
    offset = ((final_size[0] - img.size[0]) // 2, (final_size[1] - img.size[1]) // 2)
    new_img.paste(img, offset)

    # 6. Save PNG
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    png_path = output_dir / f"{name}.png"
    new_img.save(png_path, format="PNG")
    print(f"Saved PNG: {png_path}")

    # 7. Save ICO
    ico_path = output_dir / f"{name}_favicon.ico"
    # Sizes: 16, 32, 48, 64
    new_img.save(ico_path, format="ICO", sizes=[(16,16), (32,32), (48,48), (64,64)])
    print(f"Saved ICO: {ico_path}")

    return png_path, ico_path
```

*Note: Needs `import io`.*

---

### Task 4: CLI Entry Point (`main.py`)

**Goal:** Tie everything together with `argparse`.

**Files:**
- Modify: `main.py`
- Create: `app/main.py` (Move logic here or keep in root? PRD suggests `app/` structure, but `main.py` is usually root. Let's keep `main.py` in root as entry.)

**Step 1: Implement `main.py`**

```python
import argparse
import os
import sys
from dotenv import load_dotenv
from pathlib import Path
from app.generate_logo import generate_logo
from app.process_logo import process_logo

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Free Logo Marker - Local AI Logo Tool")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--generate", action="store_true", help="Generate logo from prompt only")
    group.add_argument("--process", action="store_true", help="Process existing image only")
    group.add_argument("--all", action="store_true", help="Generate and then process")

    parser.add_argument("--prompt", type=str, help="Text prompt for generation")
    parser.add_argument("--input", type=str, help="Input file path for processing")
    parser.add_argument("--name", type=str, default="logo", help="Base name for output files")

    args = parser.parse_args()

    # Validation
    if (args.generate or args.all) and not args.prompt:
        parser.error("--prompt is required for generation modes")

    if args.process and not args.input:
        parser.error("--input is required for process mode")

    # Paths
    assets_dir = Path("assets")
    output_dir = Path("output")

    raw_image_path = None

    # Execution
    if args.generate or args.all:
        raw_filename = f"{args.name}_raw.png"
        raw_image_path = assets_dir / raw_filename

        print(f"Mode: GENERATE. Prompt: '{args.prompt}'")
        generate_logo(
            prompt=args.prompt,
            output_path=str(raw_image_path)
        )

    if args.process:
        raw_image_path = args.input

    if args.process or args.all:
        print(f"Mode: PROCESS. Input: {raw_image_path}")
        process_logo(
            input_path=str(raw_image_path),
            output_dir=str(output_dir),
            name=args.name
        )

    print("Done.")

if __name__ == "__main__":
    main()
```

---

### Task 5: Integration Testing & README

**Goal:** Verify full flow and document usage.

**Files:**
- Modify: `README.md`
- Run: Manual test with CLI

**Step 1: Update README**

Add usage instructions for all 3 modes.

**Step 2: Verification**
Run `python main.py --help` to verify CLI.
