from django.contrib import admin

from .models import Comment, Group, Post, ViewPost


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "text", "pub_date", "author", "group")
    list_editable = ("group", "author")
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "slug", "description")
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Comment)
admin.site.register(ViewPost)
