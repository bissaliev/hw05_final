from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import CommentForm, PostForm
from .mixins import PostMixinListView, SearchMixin
from .models import Comment, Follow, Post

User = get_user_model()


class PostListView2(ListView):  # not
    template_name = "posts/post_list.html"
    queryset = Post.objects.select_related("author", "group").all()
    context_object_name = "posts"
    paginate_by = settings.PAGE_SIZE


class PostListView(PostMixinListView):
    """Класс представления списка постов."""

    pass


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
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Класс представление для создания поста."""

    form_class = PostForm
    template_name = "posts/create_post.html"

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        return super().form_valid(form)


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


class GroupPostListView(PostMixinListView):
    """Класс представления списка постов по определенной группе."""

    def get_queryset(self):
        return super().get_queryset().filter(group__slug=self.kwargs.get("slug"))


class PostProfileListView(PostMixinListView):
    """
    Класс представления личной страницы пользователя
    с отображением ленты его опубликованных постов.
    """

    template_name = "posts/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = get_object_or_404(User, username=self.kwargs.get("username"))
        context["author"] = author
        context["following"] = Follow.objects.filter(author=author).exists()
        return context

    def get_queryset(self):
        author = get_object_or_404(User, username=self.kwargs.get("username"))
        return author.posts.all()


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


class PostFollowListView(LoginRequiredMixin, PostMixinListView):
    """Класс представления постов избранных авторов."""

    def get_queryset(self):
        return super().get_queryset().filter(author__following__user=self.request.user)


class AddDeleteFollowing(LoginRequiredMixin, View):
    """
    Класс представление для добавления автора в избранные
    или удаления автора из избранных.
    """

    def get(self, request, username):
        author = get_object_or_404(User, username=username)
        if request.user != author:
            if not request.user.follower.filter(author=author):
                Follow.objects.create(user=request.user, author=author)
            else:
                Follow.objects.filter(user=request.user, author=author).delete()
        return redirect("posts:profile", username=username)
