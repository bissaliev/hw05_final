from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from posts.models import Post


@receiver(post_save, sender=Post)
def post_save_post(sender, instance, created, update_fields, **kwargs) -> None:
    instance.update_search_vector()


@receiver(post_delete, sender=Post)
def delete_image_on_model(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(False)
