import httpx
import os

IMGUR_CLIENT_ID = os.getenv("IMGUR_CLIENT_ID")


async def upload_image_to_imgur(image_bytes: bytes) -> str:
    if not IMGUR_CLIENT_ID:
        raise RuntimeError("IMGUR_CLIENT_ID not set in environment!")
    headers = {"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"}
    async with httpx.AsyncClient() as client:
        files = {"image": image_bytes}
        response = await client.post(
            "https://api.imgur.com/3/image", headers=headers, files=files, timeout=30
        )
        response.raise_for_status()
        data = response.json()
        if not data.get("success"):
            raise RuntimeError(f"Imgur upload failed: {data}")
        return data["data"]["link"]
