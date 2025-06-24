import os
import uuid

# Папка на VPS, где nginx или другой сервер отдает статику
VPS_IMAGE_DIR = os.getenv("VPS_IMAGE_DIR", "/var/www/foodbot_images/")
# Публичный URL, по которому доступны файлы
VPS_IMAGE_URL = os.getenv("VPS_IMAGE_URL", "http://your-vps-domain.com/images/")

async def upload_image_to_vps(image_bytes: bytes, ext: str = ".jpg") -> str:
    """
    Сохраняет изображение на VPS в папку, отдаваемую web-сервером.
    Возвращает публичный URL для доступа к файлу.
    """
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(VPS_IMAGE_DIR, filename)
    # Убедитесь, что папка существует и есть права на запись!
    with open(filepath, "wb") as f:
        f.write(image_bytes)
    return VPS_IMAGE_URL + filename

# ---
# Как использовать вместо imgur_upload:
# from vps_upload import upload_image_to_vps
# ...
# img_url = await upload_image_to_vps(file_bytes)
# answer = await analyze_food_image(img_url)
# ---

# Не забудьте настроить nginx или другой сервер так,
# чтобы файлы из VPS_IMAGE_DIR были доступны по VPS_IMAGE_URL!
