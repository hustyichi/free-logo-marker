# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

- **Install Dependencies**: `uv sync` or `pip install -e .`
- **Run (Generate & Process)**: `python main.py --all --prompt "your prompt" --name output_dir_name`
- **Run (Generate Only)**: `python main.py --generate --prompt "your prompt" --name output_dir_name`
- **Run (Process Only)**: `python main.py --process --input assets/raw_image.png --name output_dir_name`
- **Tests**: No test suite detected. Run `python main.py --help` to verify CLI availability.

## Architecture

- **Entry Point**: `main.py` handles CLI argument parsing and orchestrates the workflow.
- **Core Modules**:
  - `app/generate_logo.py`: Handles interaction with OpenAI-compatible APIs to generate images.
  - `app/process_logo.py`: Uses `rembg` for background removal and `PIL` for cropping/resizing/formatting.
- **Data Flow**:
  - Generated raw images are saved to `assets/`.
  - Processed images (PNG, ICO) are saved to `output/<name>/`.
- **Key Dependencies**: `openai` (generation), `rembg` (background removal), `pillow` (image manipulation).

## Style & Conventions

- **Python Version**: 3.10+
- **Path Handling**: Use `pathlib.Path` for all file path operations.
- **Type Hinting**: Use standard Python type hints in function signatures.
- **Configuration**: Environment variables loaded via `python-dotenv` from `.env`.
- **API**: The generation module expects an OpenAI-compatible API (supports local LLMs or paid services).
