import contextlib
import os

from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from posts.models import Post
from sorl.thumbnail import delete as thumbnail_delete
from sorl.thumbnail import get_thumbnail
from sorl.thumbnail.models import KVStore


@receiver(post_save, sender=Post)
def post_save_post(sender, instance, created, update_fields, **kwargs) -> None:
    instance.update_search_vector()


@receiver(post_delete, sender=Post)
def delete_image_on_model(sender, instance, **kwargs):
    if instance.image:
        # kvstore_entries = KVStore.objects.filter(value__icontains=instance.image.name)
        # print(kvstore_entries.__dict__)
        thumbnail_delete(instance.image)
        instance.image.delete(False)
