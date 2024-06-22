import contextlib
import io
import os

from celery import shared_task
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from PIL import Image

from .models import Post


@shared_task
def process_image(post_id, temp_image_path, image_name):
    with contextlib.suppress(Post.DoesNotExist):
        post = Post.objects.get(id=post_id)

        img = Image.open(temp_image_path)
        img_bytes = io.BytesIO()
        img.save(fp=img_bytes, format="WEBP")
        path = default_storage.save(
            f"posts/{os.path.splitext(image_name)[0]}.webp",
            ContentFile(content=img_bytes.getvalue()),
        )
        post.image.name = path
        post.save()

        os.remove(temp_image_path)
