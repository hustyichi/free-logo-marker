import base64
import os
import re
import requests
from openai import OpenAI
from pathlib import Path

def generate_logo(prompt: str, output_path: str, model: str = "gemini-3-pro-image", api_base: str = None, api_key: str = None) -> str:
    """
    Generates an image from a prompt using OpenAI-compatible API and saves it.

    Args:
        prompt: The description of the logo to generate.
        output_path: The file path where the generated image should be saved.
        model: The model name to use (default: gemini-3-pro-image).
        api_base: The base URL for the API (optional, defaults to env var or local).
        api_key: The API key (optional, defaults to env var or 'not-needed').

    Returns:
        The path to the saved image file.
    """
    # Configuration
    base_url = api_base or os.getenv("GEN_API_BASE_URL", "http://127.0.0.1:8045/v1")
    key = api_key or os.getenv("GEN_API_KEY", "not-needed")

    client = OpenAI(
        base_url=base_url,
        api_key=key
    )

    # Enforce flat, vector style in prompt as per PRD
    full_prompt = (
        f"{prompt}. "
        "Style requirements: Flat 2D vector logo, minimalist, solid white background, "
        "no shadows, high contrast, centered subject."
    )

    print(f"Generating logo with prompt: {prompt[:50]}...")
    print(f"Using model: {model} at {base_url}")

    try:
        # Call the API
        response = client.chat.completions.create(
            model=model,
            extra_body={"size": "1024x1024"}, # As per PRD 3.4
            messages=[{"role": "user", "content": full_prompt}]
        )

        # Depending on the backend, the content might be a URL or b64json
        content = response.choices[0].message.content

        # Debug print to help diagnose issues if they persist
        if not content:
            print(f"Debug: Content is empty. Full response: {response.model_dump_json()}")
        else:
            print(f"Debug: Response content preview: {content[:100]}...")

        image_url = None

        # Strategy 1: Look for Markdown image syntax ![alt](url)
        markdown_match = re.search(r'!\[.*?\]\((.*?)\)', content)
        if markdown_match:
            image_url = markdown_match.group(1)
            print("Extracted URL/URI from markdown pattern.")

        # Strategy 2: Look for http/https URL if no markdown found
        if not image_url:
            # Matches http:// or https:// followed by non-whitespace characters
            # Excludes common trailing punctuation like ) ] " '
            url_match = re.search(r'(https?://[^\s"\'\)\]>]+)', content)
            if url_match:
                image_url = url_match.group(1)
                print("Extracted HTTP URL from text.")

        # Strategy 3: Look for Data URI pattern
        if not image_url:
            # Matches data:image/...;base64, followed by base64 chars
            data_uri_match = re.search(r'(data:image/[a-zA-Z]+;base64,[a-zA-Z0-9+/=]+)', content)
            if data_uri_match:
                image_url = data_uri_match.group(1)
                print("Extracted Data URI from text.")

        # Strategy 4: Fallback - check if the entire stripped content is a URL or Data URI
        if not image_url:
            cleaned = content.strip()
            if cleaned.startswith("http") or cleaned.startswith("data:"):
                image_url = cleaned
                print("Using full content as URL/Data URI.")

        if not image_url:
             # Dump more context for debugging
             print(f"Debug: Failed to parse. Full content length: {len(content)}")
             raise ValueError(f"Could not parse image URL from response. Content preview: {content[:200]}...")

        # Download/Decode the image data
        if image_url.startswith("data:"):
            print("Processing data URI...")
            try:
                # data:image/png;base64,.....
                header, encoded = image_url.split(",", 1)
                img_data = base64.b64decode(encoded)
            except Exception as e:
                raise ValueError(f"Failed to decode base64 data URI: {e}")
        elif image_url.startswith("http"):
            print(f"Downloading image from: {image_url}")
            img_data = requests.get(image_url).content
        else:
            raise ValueError(f"Unknown image URL format: {image_url[:50]}...")

        # Ensure directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'wb') as f:
            f.write(img_data)

        print(f"Image saved to {output_path}")
        return output_path

    except Exception as e:
        print(f"Error generating logo: {e}")
        raise
