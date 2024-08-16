from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeDoneView,
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.urls import path

from . import views

app_name = "users"


urlpatterns = [
    path("signup/", views.SignUp.as_view(), name="signup"),
    path(
        "logout/",
        LogoutView.as_view(template_name="users/logged_out.html"),
        name="logout",
    ),
    path(
        "login/",
        LoginView.as_view(template_name="users/login.html"),
        name="login",
    ),
    path(
        "password_reset/",
        PasswordResetView.as_view(
            template_name="users/password_reset_form.html"
        ),
        name="password_reset_form",
    ),
    path(
        "password_reset/done/",
        PasswordResetDoneView.as_view(
            template_name="users/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "password_change/",
        PasswordChangeView.as_view(
            template_name="users/password_change_form.html"
        ),
        name="password_change_form",
    ),
    path(
        "password_change/done/",
        PasswordChangeDoneView.as_view(
            template_name="users/password_change_done.html"
        ),
        name="password_change_done",
    ),
    path(
        "reset/done/",
        PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("me/", views.ProfileView.as_view(), name="me"),
    path(
        "users/<str:username>/",
        views.ProfileDetailView.as_view(),
        name="profile",
    ),
    path("profile_edit", views.UserEditView.as_view(), name="profile_edit"),
    path("users/", views.UserListView.as_view(), name="user_list"),
    path(
        "subscriptions/",
        views.SubscriptionListView.as_view(),
        name="subscription_list",
    ),
]
