from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, View
from posts.models import Post

from .forms import CreationForm, ProfileForm

User = get_user_model()


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy("posts:index")
    template_name = "users/signup.html"


class ProfileView(View):
    def get(self, request):
        context = {
            "form": ProfileForm(instance=request.user),
            "view_posts": Post.objects.filter(view_posts__user=request.user).order_by(
                "-view_posts__date_of_viewing"
            ),
            "posts_of_user": Post.objects.filter(author=request.user).order_by(
                "-pub_date"
            ),
        }
        return render(request, "users/me.html", context)

    def post(self, request):
        user = User.objects.get(id=request.user.id)
        form = ProfileForm(request.POST, instance=user, files=request.FILES or None)
        if form.is_valid():
            form.save()
        return render(request, "users/me.html", {"user": user, "form": form})
