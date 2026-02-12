import argparse
import os
import sys
from dotenv import load_dotenv
from pathlib import Path
from loguru import logger
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
    parser.add_argument("--name", type=str, default="default", help="Output directory name under output/")

    args = parser.parse_args()

    # Validation
    if (args.generate or args.all) and not args.prompt:
        parser.error("--prompt is required for generation modes")

    if args.process and not args.input:
        parser.error("--input is required for process mode")

    # Paths
    assets_dir = Path("assets")
    output_dir = Path("output") / args.name

    # Create directories if they don't exist
    assets_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_image_path = None

    # Execution
    if args.generate or args.all:
        raw_filename = f"{args.name}_raw.png"
        raw_image_path = assets_dir / raw_filename

        logger.info(f"Mode: GENERATE. Prompt: '{args.prompt}'")
        try:
            generate_logo(
                prompt=args.prompt,
                output_path=str(raw_image_path)
            )
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            sys.exit(1)

    if args.process:
        raw_image_path = args.input

    if args.process or args.all:
        if not raw_image_path:
             logger.error("Error: No input image path defined.")
             sys.exit(1)

        logger.info(f"Mode: PROCESS. Input: {raw_image_path}")
        try:
            process_logo(
                input_path=str(raw_image_path),
                output_dir=str(output_dir)
            )
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            sys.exit(1)

    logger.success("Done.")

if __name__ == "__main__":
    main()
