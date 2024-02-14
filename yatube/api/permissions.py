from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Чтение для всех, создание только авторизированные пользователи,
    редактирование только авторы.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
