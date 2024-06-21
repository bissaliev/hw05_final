import contextlib

from celery import shared_task
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from .models import Post


@shared_task
def process_image(post_id, temp_image_path, image_name):
    with contextlib.suppress(Post.DoesNotExist):
        post = Post.objects.get(id=post_id)
        with open(temp_image_path, "rb") as temp_image:
            path = default_storage.save(
                f"posts/{image_name}", ContentFile(temp_image.read())
            )
            post.image.name = path
            post.save()

            import os

            os.remove(temp_image_path)
