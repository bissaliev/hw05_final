from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models.base import Model as Model
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, View
from posts.models import Post

from .forms import CreationForm, ProfileForm

User = get_user_model()


class SignUp(CreateView):
    """Класс представление регистрации пользователей."""

    form_class = CreationForm
    success_url = reverse_lazy("posts:index")
    template_name = "users/signup.html"


class UserEditView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    """Класс представление для редактирования профиля пользователя."""

    model = User
    template_name = "users/profile_form.html"
    form_class = ProfileForm
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


class ProfileView(View):
    """Класс представление личного кабинета пользователя."""

    def get(self, request):
        context = {
            "view_posts": Post.objects.filter(
                view_posts__user=request.user
            ).order_by("-view_posts__date_of_viewing"),
            "posts_of_user": Post.objects.filter(author=request.user).order_by(
                "-pub_date"
            ),
        }
        return render(request, "users/me.html", context)


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
            following__user__username=self.request.user.username
        )
        return queryset
