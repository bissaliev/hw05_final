import csv
import datetime

from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html

from .models import Follow


class FollowAdminForm(forms.ModelForm):
    """Форма подписки для административной панели."""

    class Meta:
        model = Follow
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get("user")
        author = cleaned_data.get("author")
        if user == author:
            raise ValidationError(
                "Пользователь не можете быть подписан на самого себя."
            )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Административная панель для модели Follow."""

    form = FollowAdminForm
    list_display = ("user", "author", "created_at")
    readonly_fields = ("created_at",)


@admin.register(get_user_model())
class UserAdmin(admin.ModelAdmin):
    """Административная панель для модели User."""

    list_display = (
        "id",
        "username",
        "first_name",
        "last_name",
        "get_subscribers_count",
        "get_views_count",
        "view_posts_link",
    )
    list_editable = ("username", "first_name", "last_name")
    save_as = True
    ordering = ("username", "first_name", "last_name")
    actions = ["export_to_csv"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related("posts", "posts__view_posts", "following")
        qs = qs.annotate(views_count=Count("posts__view_posts"))
        return qs

    @admin.display(description="Кол-во просмотров постов автора")
    def get_views_count(self, obj):
        """Количество просмотров постов автора."""
        return obj.views_count

    @admin.display(description="Кол-во подписчиков")
    def get_subscribers_count(self, obj):
        """Количество подписчиков."""
        return obj.following.count()

    @admin.display(description="Posts")
    def view_posts_link(self, obj):
        """Ссылка на список публикаций автора."""
        count = obj.posts.count()
        url = (
            reverse("admin:posts_post_changelist")
            + f"?author__id__exact={obj.id}"
        )
        return format_html(
            '<a href="{}">Просмотр публикаций ({})</a>', url, count
        )

    @admin.display(description="Экспорт в CSV")
    def export_to_csv(self, request, queryset):
        """Экспорт в CSV."""
        opts = self.model._meta
        content_disposition = f"attachment; filename={opts.app_label}.csv"
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = content_disposition
        writer = csv.writer(response)
        fields = ["username", "first_name", "last_name", "email", "birth_date"]
        writer.writerow(fields)
        for obj in queryset:
            data_row = []
            for field in fields:
                value = getattr(obj, field)
                if isinstance(value, datetime.datetime):
                    value = value.strftime("%d/%m/%Y")
                data_row.append(value)
            writer.writerow(data_row)
        return response
