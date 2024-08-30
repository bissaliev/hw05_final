from django.db.models.signals import post_delete, post_save
from django.dispatch import Signal, receiver
from posts.models import Post, ViewPost
from sorl.thumbnail import delete as thumbnail_delete

from .utils import cache_post_delete, get_client_ip


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


post_view_signal = Signal()


@receiver(post_view_signal)
def create_post_view(sender, instance, request, **kwargs):
    """При просмотре страницы определенного создается запись в БД."""
    ViewPost.objects.get_or_create(
        post=instance, ip_address=get_client_ip(request)
    )
