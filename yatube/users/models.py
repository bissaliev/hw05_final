from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class UserQueryset(models.QuerySet):
    def get_is_subscribed(self):
        return self.annotate(
            is_subscribed=models.Exists(
                Follow.objects.filter(author=models.OuterRef("pk")).values(
                    "id"
                )
            )
        )

    def get_subscriptions_count(self):
        """Количество подписок."""
        return self.annotate(subscriptions_count=models.Count("follower"))

    def get_subscribers_count(self):
        """Количество подписчиков."""
        return self.annotate(subscribers_count=models.Count("following"))


class CustomUserManager(UserManager):
    def get_queryset(self) -> models.QuerySet:
        return UserQueryset(self.model, using=self._db)

    def get_is_subscribed(self):
        return self.get_queryset().get_is_subscribed()

    def get_subscriptions_count(self):
        return self.get_queryset().get_subscriptions_count()

    def get_subscribers_count(self):
        return self.get_queryset().get_subscribers_count()

    def get_posts_count(self):
        return self.get_queryset().get_posts_count()


class User(AbstractUser):
    """Кастомная модель User."""

    avatar = models.ImageField(
        "Фотография", upload_to="users/%Y/%m/%d", null=True, blank=True
    )
    birth_date = models.DateField("Дата рождения", blank=True, null=True)

    objects = CustomUserManager()


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
