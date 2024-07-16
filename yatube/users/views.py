from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, View
from posts.models import Post

from .forms import CreationForm, ProfileForm

User = get_user_model()


class SignUp(CreateView):
    """Класс представление регистрации пользователей."""

    form_class = CreationForm
    success_url = reverse_lazy("posts:index")
    template_name = "users/signup.html"


class UserUpdateView(View):
    """Класс представление для редактирования профиля пользователя."""

    def get(self, request):
        form = ProfileForm(instance=request.user)
        context = {"form": form}
        return render(request, "users/profile_form.html", context)

    def post(self, request):
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
        context = {"form": form}
        return render(request, "users/profile_form.html", context)


class ProfileView(View):
    """Класс представление личного кабинета пользователя."""

    def get(self, request):
        context = {
            "view_posts": Post.objects.filter(view_posts__user=request.user).order_by(
                "-view_posts__date_of_viewing"
            ),
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
