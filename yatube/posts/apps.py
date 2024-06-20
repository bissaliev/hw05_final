from django.apps import AppConfig


class PostsConfig(AppConfig):
    name = "posts"

    def ready(self) -> None:
        import posts.signals
