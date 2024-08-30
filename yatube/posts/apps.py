from django.apps import AppConfig


class PostsConfig(AppConfig):
    name = "posts"
    verbose_name = "Публикации"

    def ready(self) -> None:
        import posts.signals  # noqa
