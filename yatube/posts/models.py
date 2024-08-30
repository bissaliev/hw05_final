from django.contrib.auth import get_user_model
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.db import models
from django.db.models import Count
from django.urls import reverse

from .fields import WEBPField

User = get_user_model()


class PostQuerySet(models.QuerySet):
    def get_views_count(self):
        """Количество просмотров поста."""
        queryset = self.annotate(
            views_count=Count("view_posts", distinct=True)
        )
        return queryset

    def get_count_posts_of_author(self):
        """Количество постов у определенного автора."""
        queryset = self.annotate(
            count_posts_of_author=Count("author__posts", distinct=True)
        )
        return queryset


class PostManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return PostQuerySet(self.model, using=self._db)

    def get_views_count(self):
        """Количество просмотров поста."""
        return self.get_queryset().get_views_count()

    def get_count_posts_of_author(self):
        """Количество постов у определенного автора."""
        return self.get_queryset().get_count_posts_of_author()


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

    title = models.CharField(
        "Заголовок", max_length=150, blank=True, null=True
    )
    text = models.TextField(verbose_name="текст поста")
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name="дата публикации"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="имя автора",
    )
    group = models.ForeignKey(
        "Group",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="posts",
        verbose_name="название группы",
    )
    image = WEBPField("Картинка", upload_to="posts/", blank=True)
    search_vector = SearchVectorField(null=True)
    objects = PostManager()

    class Meta:
        indexes = [
            GinIndex(fields=["search_vector"]),
        ]
        ordering = ["-pub_date"]
        verbose_name = "Пост"
        verbose_name_plural = "Посты"

    def __str__(self):
        return self.text[:15]

    def get_absolute_url(self):
        return reverse("posts:post_detail", kwargs={"post_id": self.pk})

    def update_search_vector(self) -> None:
        qs = Post.objects.filter(pk=self.pk)
        qs.update(
            search_vector=SearchVector("title", "text", config="russian")
        )


class Comment(models.Model):
    """Модель комментариев."""

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="пост",
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


class ViewPost(models.Model):
    """Модель для отслеживания уникальных просмотров пользователем."""

    post = models.ForeignKey(
        to=Post, on_delete=models.CASCADE, related_name="view_posts"
    )
    user = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="view_posts",
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    date_of_viewing = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.ip_address} просмотрел {self.post} - {self.date_of_viewing}"

    class Meta:
        verbose_name = "Просмотр"
        verbose_name_plural = "Просмотры"
        constraints = [
            models.UniqueConstraint(
                fields=("post", "user"), name="unique_view_post"
            )
        ]
