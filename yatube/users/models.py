from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель User."""

    avatar = models.ImageField(
        "Фотография", upload_to="users/%Y/%m/%d", null=True, blank=True
    )
    birth_date = models.DateField("Дата рождения", blank=True, null=True)

    @property
    def subscribers_count(self):
        """Количество подписчиков."""
        return self.following.count()

    @property
    def subscriptions_count(self):
        """Количество подписок."""
        return self.follower.count()

    @property
    def posts_count(self):
        """Количество постов."""
        return self.posts.count()


class Follow(models.Model):
    """Модель подписок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="автор поста",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_follow"
            )
        ]
