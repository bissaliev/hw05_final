from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet, CustomUserViewSet, GroupViewSet, PostViewSet

router = DefaultRouter()
router.register(r"users", CustomUserViewSet, basename="users")
router.register(
    r"posts/(?P<post_id>\d+)/comments", CommentViewSet, basename="comments"
)
router.register(r"posts", PostViewSet, basename="posts")
router.register(r"groups", GroupViewSet, basename="groups")


urlpatterns = [
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
