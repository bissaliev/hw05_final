from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.temp import NamedTemporaryFile
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DeleteView, DetailView, ListView, UpdateView

from .forms import CommentForm, FollowForm, PostForm
from .mixins import CacheMixin, PostMixinListView, SearchMixin
from .models import Comment, Follow, Post
from .tasks import process_image

User = get_user_model()


class PostListView(CacheMixin, PostMixinListView):
    """Класс представления списка постов."""

    def get_queryset(self):
        queryset = super().get_queryset()
        cache_name = "index_cache"
        return self.get_cache(queryset, cache_name, self.cache_timeout)


class SearchPost(SearchMixin, PostMixinListView):
    """Класс представления для поиска постов."""

    pass


class PostDetailView(DetailView):
    """Класс представления определенного поста."""

    model = Post
    template_name = "posts/post_detail.html"
    pk_url_kwarg = "post_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comments"] = Comment.objects.filter(post_id=self.kwargs.get("post_id"))
        context["form"] = CommentForm(self.request.POST or None)
        context["form_follow"] = FollowForm(initial={"author": self.object.author})
        context["is_subscribed"] = self.request.user.follower.filter(
            author=self.object.author
        ).exists()
        return context


class PostCreateView(LoginRequiredMixin, View):
    """Класс представление для создания поста."""

    def get(self, request):
        form = PostForm()
        return render(request, "posts/create_post.html", {"form": form})

    def post(self, request):
        img = request.FILES.get("image", None)
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            if img:
                temp_image = NamedTemporaryFile(delete=False)
                temp_image.write(img.read())
                temp_image.flush()
                process_image.delay(post.id, temp_image.name, img.name)
                return redirect("posts:post_detail", post.id)
        return render(request, "posts/create_post.html", {"form": form})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    """Класс представление для редактирования поста."""

    form_class = PostForm
    model = Post
    template_name = "posts/create_post.html"
    pk_url_kwarg = "post_id"
    success_url = reverse_lazy("posts:index")  # перенаправить на пост


class PostDeleteView(LoginRequiredMixin, DeleteView):
    """Класс для удаления автором своего поста."""

    model = Post
    pk_url_kwarg = "post_id"
    success_url = reverse_lazy("posts:index")


class GroupPostListView(CacheMixin, PostMixinListView):
    """Класс представления списка постов по определенной группе."""

    def get_queryset(self):
        slug = self.kwargs.get("slug")
        queryset = super().get_queryset().filter(group__slug=slug)
        cache_name = f"posts_of_group_cache_{slug}"
        return self.get_cache(queryset, cache_name, self.cache_timeout)


class PostProfileListView(ListView):
    """
    Класс представления личной страницы пользователя
    с отображением ленты его опубликованных постов.
    """

    template_name = "posts/profile.html"
    paginate_by = 8
    queryset = Post.objects.select_related("group")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = get_object_or_404(User, username=self.kwargs.get("username"))
        context["author"] = author
        context["form"] = FollowForm(initial={"author": author})
        context["is_subscribed"] = self.request.user.follower.filter(
            author=author
        ).exists()
        return context

    def get_queryset(self):
        username = self.kwargs.get("username")
        queryset = super().get_queryset()
        return queryset.filter(author__username=username).prefetch_related("author")


class AddCommentView(LoginRequiredMixin, View):
    """Класс добавления нового комментария к определенному посту."""

    def post(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        form = CommentForm(request.POST or None)
        if form.is_valid() and request.user.is_authenticated:
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            form.save()
        return redirect("posts:post_detail", post_id=post_id)


class PostFollowListView(LoginRequiredMixin, CacheMixin, PostMixinListView):
    """Класс представления постов избранных авторов."""

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset().filter(author__following__user=user)
        cache_name = f"post_follow_cache_{user.id}"
        return self.get_cache(queryset, cache_name, self.cache_timeout)


class AddDeleteFollowing(LoginRequiredMixin, View):
    """
    Класс представление для добавления автора в избранные
    или удаления автора из избранных.
    """

    def post(self, request):
        author = get_object_or_404(User, pk=request.POST.get("author"))
        instance, created = Follow.objects.get_or_create(
            author=author, user=request.user
        )
        if not created:
            instance.delete()
        return redirect(request.META.get("HTTP_REFERER", "/"))
