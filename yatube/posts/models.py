from django.db import models

from django.contrib.auth import get_user_model
from django.urls import reverse


User = get_user_model()


class Group(models.Model):
    """Модель групп."""

    title = models.CharField(max_length=200, verbose_name="название")
    description = models.TextField(verbose_name="описание")
    slug = models.SlugField(
        max_length=100, unique=True, verbose_name="имя страницы группы"
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


class Post(models.Model):
    """Модель постов."""

    title = models.CharField("Заголовок", max_length=150, blank=True, null=True)
    text = models.TextField(verbose_name="текст поста")
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name="дата публикации")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts", verbose_name="имя автора"
    )
    group = models.ForeignKey(
        "Group",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="posts",
        verbose_name="название группы",
    )
    image = models.ImageField("Картинка", upload_to="posts/", blank=True)

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = "Пост"
        verbose_name_plural = "Посты"

    def __str__(self):
        return self.text[:15]

    def get_absolute_url(self):
        return reverse("posts:post_detail", kwargs={"post_id": self.pk})


class Comment(models.Model):
    """Модель комментариев."""

    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments", verbose_name="пост"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comment",
        verbose_name="имя автора",
    )
    text = models.TextField(verbose_name="текст комментария")
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ["-created"]
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"


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
            models.UniqueConstraint(fields=["user", "author"], name="unique_follow")
        ]
