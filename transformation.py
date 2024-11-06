from wand.image import Image
import os

def is_format_supported(format: str) -> bool:
    """
    Checks if the destination image format is supported by Wand (ImageMagick).
    
    Args:
    - format (str): Desired output format, e.g., 'jpeg', 'png', 'webp'.
    
    Returns:
    - bool: True if the format is supported, False otherwise.
    """
    # temporary 
    supported_formats = {"jpeg", "jpg", "png", "webp", "tiff", "bmp", "gif", "heic"}
    return format.lower() in supported_formats

def convert_image(src_path: str, dest_folder: str, output_format: str) -> str:
    """
    Converts an image from its current format to the specified output format.
    
    Args:
    - src_path (str): The path to the source image file.
    - dest_folder (str): The folder where the converted image will be saved.
    - output_format (str): The desired output format, e.g., 'jpeg', 'png', 'webp'.
    
    Returns:
    - str: The path to the converted image if successful; None if there's an error.
    """
    if not is_format_supported(output_format):
        print(f"Unsupported output format: {output_format}")
        return None
    
    # Ensure the destination folder exists
    os.makedirs(dest_folder, exist_ok=True)
    
    # Construct destination path
    base_name = os.path.splitext(os.path.basename(src_path))[0]
    dest_path = os.path.join(dest_folder, f"{base_name}.{output_format.lower()}")

    try:
        with Image(filename=src_path) as img:
            img.format = output_format.lower()
            img.save(filename=dest_path)
            print(f"Image converted and saved at: {dest_path}")
            return dest_path
    except Exception as e:
        print(f"Error converting image: {e}")
        return None

