import io
from PIL import Image

MAX_FILE_SIZE = 200 * 1024  # 200 KB
MAX_DIMENSION = 256  # 128 pixels max width and height

async def validate_image(attachment):
    if attachment.size > MAX_FILE_SIZE:
        return False, "❌ Image file size exceeds 60 KB."

    img_bytes = await attachment.read()
    try:
        with Image.open(io.BytesIO(img_bytes)) as img:
            if img.width > MAX_DIMENSION or img.height > MAX_DIMENSION:
                return False, "❌ Image dimensions must be 128x128 pixels or smaller."
    except Exception:
        return False, "❌ Could not process image. Please upload a valid image file."

    return True, "Image is valid."
