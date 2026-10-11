import os
from typing import List, Optional
from PIL import Image
from pillow_heif import register_heif_opener
import logging

# Adds .heic/.heif read and write support to Pillow
register_heif_opener()


class ImageConverter:
    # Ordered, so the format list looks the same on every run
    SUPPORTED_FORMATS = ("jpg", "jpeg", "png", "webp", "tiff", "bmp", "gif", "heic")

    # File extensions that can be opened as source images
    INPUT_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif", ".bmp", ".gif", ".heic", ".heif")

    # Extension -> Pillow format name
    PILLOW_FORMATS = {
        "jpg": "JPEG",
        "jpeg": "JPEG",
        "png": "PNG",
        "webp": "WEBP",
        "tiff": "TIFF",
        "bmp": "BMP",
        "gif": "GIF",
        "heic": "HEIF",
    }

    # Formats that can hold several frames (animations / multi-page files)
    MULTI_FRAME_FORMATS = {"GIF", "WEBP", "TIFF"}

    # Formats that can carry EXIF metadata
    EXIF_FORMATS = {"JPEG", "PNG", "WEBP", "TIFF", "HEIF"}

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
    def is_image_file(cls, path: str) -> bool:
        """
        Checks if a file looks like a supported source image, based on its extension.
        """
        return path.lower().endswith(cls.INPUT_EXTENSIONS)

    @classmethod
    def find_images(cls, folder: str) -> List[str]:
        """
        Returns every supported image inside a folder and its sub-folders, sorted.
        """
        found = []
        for root, _, names in os.walk(folder):
            found.extend(os.path.join(root, name) for name in names if cls.is_image_file(name))
        return sorted(found)

    @staticmethod
    def _unique_path(path: str) -> str:
        """
        Returns a path that does not exist yet, so nothing gets overwritten.
        """
        if not os.path.exists(path):
            return path

        root, ext = os.path.splitext(path)
        counter = 1
        while os.path.exists(f"{root} ({counter}){ext}"):
            counter += 1
        return f"{root} ({counter}){ext}"

    @staticmethod
    def _prepare(img: Image.Image, pillow_format: str) -> Image.Image:
        """
        Converts the image to a color mode the output format can store.
        """
        has_alpha = img.mode in ("RGBA", "LA", "PA") or "transparency" in img.info

        if pillow_format == "JPEG":
            if has_alpha:
                # JPEG has no transparency, flatten onto a white background
                rgba = img.convert("RGBA")
                background = Image.new("RGB", rgba.size, (255, 255, 255))
                background.paste(rgba, mask=rgba.getchannel("A"))
                return background
            if img.mode not in ("RGB", "L", "CMYK"):
                return img.convert("RGB")
            return img

        if img.mode not in ("1", "L", "P", "RGB", "RGBA"):
            return img.convert("RGBA" if has_alpha else "RGB")
        return img

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

        output_format = output_format.lower()
        pillow_format = cls.PILLOW_FORMATS[output_format]
        dest_path = None

        try:
            # Ensure the destination folder exists
            os.makedirs(dest_folder, exist_ok=True)

            # Construct destination path
            base_name = os.path.splitext(os.path.basename(src_path))[0]
            dest_path = cls._unique_path(os.path.join(dest_folder, f"{base_name}.{output_format}"))

            with Image.open(src_path) as img:
                save_args = {}
                exif = img.info.get("exif")
                if exif and pillow_format in cls.EXIF_FORMATS:
                    save_args["exif"] = exif

                if getattr(img, "n_frames", 1) > 1 and pillow_format in cls.MULTI_FRAME_FORMATS:
                    # Keep every frame of animated / multi-page images
                    img.save(dest_path, format=pillow_format, save_all=True, **save_args)
                else:
                    cls._prepare(img, pillow_format).save(dest_path, format=pillow_format, **save_args)

            logging.info(f"Image converted and saved at: {dest_path}")
            return dest_path
        except Exception as e:
            logging.error(f"Error converting image {src_path}: {e}")
            # Don't leave a half-written file behind
            if dest_path and os.path.exists(dest_path):
                try:
                    os.remove(dest_path)
                except OSError:
                    pass
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
