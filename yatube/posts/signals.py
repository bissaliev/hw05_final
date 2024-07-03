from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from posts.models import Post
from sorl.thumbnail import delete as thumbnail_delete

from .utils import cache_post_delete


@receiver(post_save, sender=Post)
def post_save_post(instance, **kwargs) -> None:
    """
    Сигнал инвалидирует кеш модели Post;
    Обновляет объект SearchVectorField.
    """
    instance.update_search_vector()
    cache_post_delete(instance)


@receiver(post_delete, sender=Post)
def delete_image_on_model(instance, **kwargs):
    """
    Сигнал инвалидирует кеш модели Post;
    Удаляет кеш-миниатюры thumbnail.
    """
    cache_post_delete(instance)
    if instance.image:
        thumbnail_delete(instance.image)
        instance.image.delete(False)
