from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import filters
from rest_framework import permissions

from posts.models import Post, Group, Comment, Follow
from .serializers import (
    PostSerializer,
    GroupSerializer,
    CommentSerializer,
    FollowSerializer,
)
from .permissions import IsAuthorOrReadOnly
from .mixins import CreateListViewSet

User = get_user_model()


class PostViewSet(ModelViewSet):
    """Вьюсет для постов."""

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrReadOnly]
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


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


class FollowViewSet(CreateListViewSet):
    """Вьюсет для подписок."""

    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("following__username",)

    def get_queryset(self):
        user = get_object_or_404(User, id=self.request.user.id)
        return user.follower.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
