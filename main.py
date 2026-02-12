import argparse
import os
import sys
import re
from dotenv import load_dotenv
from pathlib import Path
from loguru import logger
from app.generate_logo import generate_raw_image, generate_product_logo
from app.process_logo import process_logo

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Free Logo Marker - Local AI Logo Tool")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--generate", action="store_true", help="Generate logo from prompt only")
    group.add_argument("--process", action="store_true", help="Process existing image only")
    group.add_argument("--all", action="store_true", help="Generate and then process")

    # Raw generation
    parser.add_argument("--prompt", type=str, help="Text prompt for raw generation")

    # Product generation
    parser.add_argument("--product-name", type=str, help="Name of the product")
    parser.add_argument("--product-desc", type=str, help="Description of the product")
    parser.add_argument("--style", type=str, help="Visual style requirements (optional)")

    parser.add_argument("--input", type=str, help="Input file path for processing")
    parser.add_argument("--name", type=str, default="default", help="Output directory name under output/")

    args = parser.parse_args()

    # Validation & Logic setup
    is_generation = args.generate or args.all

    if is_generation:
        if args.product_name:
            if not args.product_desc:
                parser.error("--product-desc is required when --product-name is provided")
            # If name is default, try to use product name
            if args.name == "default":
                # Sanitize product name: lowercase, replace non-alphanumeric with _, strip
                sanitized = re.sub(r'[^a-z0-9]+', '_', args.product_name.lower()).strip('_')
                if sanitized:
                    args.name = sanitized
        elif not args.prompt:
            parser.error("--prompt is required if --product-name is not provided")

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
    if is_generation:
        raw_filename = f"{args.name}_raw.png"
        raw_image_path = assets_dir / raw_filename

        try:
            if args.product_name:
                logger.info(f"Mode: PRODUCT GENERATION. Product: '{args.product_name}'")
                generate_product_logo(
                    product_name=args.product_name,
                    product_desc=args.product_desc,
                    style=args.style,
                    output_path=str(raw_image_path)
                )
            else:
                logger.info(f"Mode: RAW GENERATION. Prompt: '{args.prompt}'")
                generate_raw_image(
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
