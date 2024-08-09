from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef
from django.shortcuts import get_list_or_404, get_object_or_404
from djoser.views import UserViewSet
from posts.models import Comment, Group, Post
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from users.models import Follow

from .permissions import IsAuthorOrReadOnly
from .serializers import (
    CommentSerializer,
    CustomUserSerializer,
    GroupSerializer,
    PostDetailSerializer,
    PostSerializer,
    SubscribeSerializer,
)

User = get_user_model()


class PostViewSet(ModelViewSet):
    """Вьюсет для постов."""

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrReadOnly]
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PostDetailSerializer
        return super().get_serializer_class()


class GroupViewSet(ReadOnlyModelViewSet):
    """Вьюсет для групп."""

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthorOrReadOnly]


class CommentViewSet(ModelViewSet):
    """Вьюсет для комментариев."""

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrReadOnly]

    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs.get("post_id"))
        return post.comments.all()

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs.get("post_id"))
        serializer.save(author=self.request.user, post=post)


class CustomUserViewSet(UserViewSet):
    """Вьюсет для пользователей."""

    queryset = User.objects.all().annotate(
        is_subscribed=Exists(Follow.objects.filter(user=OuterRef("pk")))
    )
    serializer_class = CustomUserSerializer

    @action(methods=["post", "delete"], detail=True)
    def subscribe(self, request, id):
        """Подписаться или отписаться от пользователя."""
        author = get_object_or_404(User, id=id)
        if request.user == author:
            return Response(
                {"error": "Нельзя подписаться на самого себя."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.method == "POST":
            subscribe, created = Follow.objects.get_or_create(
                user=request.user, author=author
            )
            if created:
                serializer = SubscribeSerializer(subscribe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(
                {"error": "Вы уже подписаны на этого пользователя."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        get_object_or_404(Follow, user=request.user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["GET"], detail=False)
    def subscriptions(self, request):
        """Получить список подписок."""
        subscriptions = get_list_or_404(Follow, user=request.user)
        serializers = SubscribeSerializer(subscriptions, many=True)
        return Response(serializers.data)
