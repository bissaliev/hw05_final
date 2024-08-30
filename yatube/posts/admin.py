from django.contrib import admin

from .models import Comment, Group, Post, ViewPost


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Административная панель для модели Post."""

    list_display = ("title", "pub_date", "author", "group", "get_views_count")
    list_editable = ("group", "author")
    search_fields = ("title",)
    list_filter = ("pub_date",)
    ordering = ("-pub_date", "title", "author")
    empty_value_display = "-пусто-"
    list_select_related = ("author", "group")

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.get_views_count()
        return queryset

    @admin.display(description="Кол-во просмотров")
    def get_views_count(self, obj):
        """Количество просмотров поста."""
        return obj.views_count


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """Административная панель для модели Group."""

    list_display = ("pk", "title", "slug", "description", "get_posts_count")
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}

    @admin.display(description="Кол-во постов")
    def get_posts_count(self, obj):
        """Количество постов группы."""
        return obj.posts.count()

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related("posts")
        return queryset


admin.site.register(Comment)
admin.site.register(ViewPost)
