from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from posts.models import Comment, Group, Post
from rest_framework import serializers
from users.models import Follow

from .fields import Base64ImageField

User = get_user_model()


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


class AuthorOfPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username")


class GroupSerializer(serializers.ModelSerializer):
    """Сериализатор для групп."""

    class Meta:
        fields = ("id", "title", "slug", "description")
        model = Group


class GroupOfPostSerializer(serializers.ModelSerializer):
    """Сериализатор для групп."""

    title = serializers.ReadOnlyField()
    slug = serializers.SlugField(required=False)

    class Meta:
        fields = ("title", "slug")
        model = Group


class CommentCreateSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ("text", "post", "author")
        read_only_fields = ("post",)


class PostSerializer(serializers.ModelSerializer):
    """Сериализатор для списков постов."""

    author = AuthorOfPostSerializer(read_only=True)
    group = GroupOfPostSerializer(read_only=True)
    views_count = serializers.IntegerField()

    class Meta:
        fields = (
            "id",
            "title",
            "text",
            "author",
            "pub_date",
            "image",
            "group",
            "views_count",
        )
        model = Post


class PostCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновление постов."""

    author = AuthorOfPostSerializer(read_only=True)
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

    author = AuthorOfPostSerializer(read_only=True)
    group = GroupOfPostSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    views_count = serializers.IntegerField()

    class Meta:
        fields = (
            "id",
            "title",
            "text",
            "author",
            "pub_date",
            "image",
            "group",
            "views_count",
            "comments",
        )
        model = Post


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
