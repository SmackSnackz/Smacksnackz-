#!/usr/bin/env python3

from PIL import Image
import sys

def create_favicon(input_path, output_path, size=32):
    """Create a favicon from an input image"""
    try:
        # Open the input image
        with Image.open(input_path) as img:
            print(f"Original image size: {img.size}")
            print(f"Original image mode: {img.mode}")
            
            # Convert to RGBA if not already
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Resize to favicon size (32x32) with high quality resampling
            favicon = img.resize((size, size), Image.Resampling.LANCZOS)
            
            # Save as ICO format
            favicon.save(output_path, format='ICO', sizes=[(size, size)])
            print(f"✅ Successfully created favicon: {output_path}")
            return True
            
    except Exception as e:
        print(f"❌ Error creating favicon: {str(e)}")
        return False

if __name__ == "__main__":
    input_file = "/app/frontend/public/assets/logo.png"
    output_file = "/app/frontend/public/favicon.ico"
    
    success = create_favicon(input_file, output_file)
    sys.exit(0 if success else 1)