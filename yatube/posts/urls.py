from django.urls import path

from . import views

app_name = "posts"

urlpatterns = [
    path("", views.PostListView.as_view(), name="index"),
    path("group/<slug:slug>/", views.GroupPostListView.as_view(), name="post_of_group"),
    path(
        "posts/profile/<str:username>/",
        views.PostProfileListView.as_view(),
        name="profile",
    ),
    path("posts/<int:post_id>/", views.PostDetailView.as_view(), name="post_detail"),
    path("create/", views.PostCreateView.as_view(), name="post_create"),
    path("posts/<int:post_id>/edit/", views.PostUpdateView.as_view(), name="post_edit"),
    path(
        "posts/<int:post_id>/delete/",
        views.PostDeleteView.as_view(),
        name="post_delete",
    ),
    path("search/", views.SearchPost.as_view(), name="search"),
    path("follow/", views.PostFollowListView.as_view(), name="follow_index"),
    path(
        "profile/follow/",
        views.AddDeleteFollowing.as_view(),
        name="profile_follow",
    ),
    path(
        "comments/<int:pk>/delete/",
        views.CommentDeleteView.as_view(),
        name="comment_delete",
    ),
    path(
        "comments/<int:pk>/edit/",
        views.CommentEditView.as_view(),
        name="comment_edit",
    ),
]
