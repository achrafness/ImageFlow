import os
from typing import List, Optional
from wand.image import Image
import logging

class ImageConverter:
    SUPPORTED_FORMATS = {"jpeg", "jpg", "png", "webp", "tiff", "bmp", "gif", "heic"}

    @classmethod
    def is_format_supported(cls, format: str) -> bool:
        """
        Checks if the destination image format is supported.
        
        Args:
        - format (str): Desired output format
        
        Returns:
        - bool: True if the format is supported, False otherwise.
        """
        return format.lower() in cls.SUPPORTED_FORMATS

    @classmethod
    def convert_image(cls, src_path: str, dest_folder: str, output_format: str) -> Optional[str]:
        """
        Converts an image from its current format to the specified output format.
        
        Args:
        - src_path (str): The path to the source image file.
        - dest_folder (str): The folder where the converted image will be saved.
        - output_format (str): The desired output format
        
        Returns:
        - str: The path to the converted image if successful; None if there's an error.
        """
        # Validate input
        if not os.path.exists(src_path):
            logging.error(f"Source file does not exist: {src_path}")
            return None
        
        if not cls.is_format_supported(output_format):
            logging.error(f"Unsupported output format: {output_format}")
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
                logging.info(f"Image converted and saved at: {dest_path}")
                return dest_path
        except Exception as e:
            logging.error(f"Error converting image {src_path}: {e}")
            return None

    @classmethod
    def batch_convert(cls, src_paths: List[str], dest_folder: str, output_format: str) -> List[Optional[str]]:
        """
        Batch convert multiple images.
        
        Args:
        - src_paths (List[str]): List of source image paths
        - dest_folder (str): Destination folder for converted images
        - output_format (str): Desired output format
        
        Returns:
        - List of converted image paths (None for failed conversions)
        """
        return [cls.convert_image(path, dest_folder, output_format) for path in src_paths]