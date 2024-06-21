from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, View

from .forms import CreationForm, ProfileForm

User = get_user_model()


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy("posts:index")
    template_name = "users/signup.html"


class ProfileView(View):
    def get(self, request):
        user = User.objects.get(id=request.user.id)
        form = ProfileForm(instance=user)
        return render(request, "users/profile.html", {"user": user, "form": form})

    def post(self, request):
        user = User.objects.get(id=request.user.id)
        form = ProfileForm(request.POST, instance=user, files=request.FILES or None)
        if form.is_valid():
            form.save()
        return render(request, "users/profile.html", {"user": user, "form": form})
