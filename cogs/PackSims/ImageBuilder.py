from PIL import Image
import io
import aiohttp
import math


async def build_image(images_url: list):
    '''Coroutine. Returns a stiched n x 4 PIL image object of the given image urls. User is responsible for closing the returned image.'''
    images_bytes = []
    async with aiohttp.ClientSession() as session:
        for url in images_url:
            async with session.get(url) as response:
                images_bytes.append(Image.open(io.BytesIO(await response.read())))

    max_width = max(img.size[0] for img in images_bytes)
    max_height = max(img.size[1] for img in images_bytes)

    # The resulting image must be ceiled up so that for example:
    # 8 has 2 rows, 4 columns
    # 7 has 2 rows, 4 columns,
    # 9 has 3 rows, 4 columns
    outp_width = max_width * 4
    outp_height = max_height * math.ceil(len(images_bytes) / 4)
    outp = Image.new(mode='RGBA', size=(outp_width, outp_height), color=(0, 0, 0, 0))  # 0,0,0,0 sets it to transparent , default is full black, must be saved as png to keep transparency

    width_pos = 0
    height_pos = 0
    for img in images_bytes:
        outp.paste(im=img, box=(width_pos, height_pos))
        if (width_pos + width_pos) > outp_width:
            height_pos += max_height
            width_pos = 0
        else:
            width_pos += max_width

    for img in images_bytes:
        img.close()

    return outp