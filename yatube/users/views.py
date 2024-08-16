from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models.base import Model as Model
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
)
from posts.forms import FollowForm
from posts.models import Post

from .forms import ProfileEditForm, RegisterForm

User = get_user_model()


class SignUp(CreateView):
    """Класс представление регистрации пользователей."""

    form_class = RegisterForm
    success_url = reverse_lazy("posts:index")
    template_name = "users/signup.html"


class UserEditView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    """Класс представление для редактирования профиля пользователя."""

    model = User
    template_name = "users/profile_form.html"
    form_class = ProfileEditForm
    success_message = "Ваши данные обновлены!"

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)

    def get_success_url(self) -> str:
        return reverse("users:me")


class ProfileView(LoginRequiredMixin, DetailView):
    """Класс представление личного кабинета пользователя."""

    model = User
    template_name = "users/me.html"

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context |= {
            "view_posts": Post.objects.filter(
                view_posts__user__id=self.user_id
            ).order_by("-view_posts__date_of_viewing"),
            "posts_of_user": Post.objects.filter(
                author__id=self.user_id
            ).order_by("-pub_date"),
        }
        return context


class ProfileDetailView(LoginRequiredMixin, ListView):
    """
    Класс представления личной страницы пользователя
    с отображением ленты его опубликованных постов.
    """

    template_name = "users/user_detail.html"
    paginate_by = settings.PAGE_SIZE
    queryset = Post.objects.select_related("group")
    context_object_name = "posts"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "author": self.author,
                "form": FollowForm(initial={"author": self.author}),
                "is_subscribed": self.request.user.is_authenticated
                and self.author.is_subscribed,
            }
        )
        return context

    def get(self, request, *args, **kwargs):
        username = self.kwargs.get("username")
        if username == request.user.username:
            return redirect("users:me")
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        username = self.kwargs.get("username")
        self.author = get_object_or_404(
            User.objects.get_is_subscribed(),
            username=username,
        )
        return self.author.posts.select_related("group")


class UserListView(ListView):
    """Класс представление списка всех пользователей."""

    model = User
    paginate_by = 8


class SubscriptionListView(LoginRequiredMixin, ListView):
    """Класс представление подписок пользователей."""

    model = User
    paginate_by = 8

    def get_queryset(self):
        queryset = User.objects.filter(
            following__user__id=self.request.user.id
        )
        return queryset
