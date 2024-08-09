import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from posts.models import Comment, Group, Post
from rest_framework import serializers
from users.models import Follow

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """
    Кастомный тип поля ImageField,который принимает
    закодированное в формате base64 изображение,
    декодирует и сохраняет его на сервере.
    """

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field="username"
    )

    class Meta:
        fields = (
            "id",
            "author",
            "text",
            "created",
        )
        model = Comment


class PostSerializer(serializers.ModelSerializer):
    """Сериализатор для списков постов."""

    author = serializers.SlugRelatedField(
        slug_field="username", read_only=True
    )
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        fields = (
            "id",
            "title",
            "text",
            "author",
            "pub_date",
            "image",
            "group",
        )
        model = Post


class PostDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального просмотра постов."""

    author = serializers.SlugRelatedField(
        slug_field="username", read_only=True
    )
    image = Base64ImageField(required=False, allow_null=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        fields = (
            "id",
            "title",
            "text",
            "author",
            "pub_date",
            "image",
            "group",
            "comments",
        )
        model = Post


class GroupSerializer(serializers.ModelSerializer):
    """Сериализатор для групп."""

    class Meta:
        fields = "__all__"
        model = Group


class CustomUserSerializer(UserSerializer):
    """Сериализатор для пользователя."""

    is_subscribed = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "birth_date",
            "avatar",
            "is_subscribed",
            "posts_count",
            "subscribers_count",
            "subscriptions_count",
        )


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки."""

    id = serializers.ReadOnlyField(source="author.id")
    username = serializers.ReadOnlyField(source="author.username")
    first_name = serializers.ReadOnlyField(source="author.first_name")
    last_name = serializers.ReadOnlyField(source="author.last_name")
    email = serializers.ReadOnlyField(source="author.email")
    birth_date = serializers.ReadOnlyField(source="author.birth_date")
    avatar = serializers.ImageField(source="author.avatar")
    posts_count = serializers.ReadOnlyField(source="author.posts_count")
    subscribers_count = serializers.ReadOnlyField(
        source="author.subscribers_count"
    )
    subscriptions_count = serializers.ReadOnlyField(
        source="author.subscriptions_count"
    )

    class Meta:
        model = Follow
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "birth_date",
            "avatar",
            "posts_count",
            "subscribers_count",
            "subscriptions_count",
        )
