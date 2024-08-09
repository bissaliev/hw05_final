from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import (
    Count,
    Exists,
    OuterRef,
    Prefetch,
)
from django.forms import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
)
from django.views.generic.detail import SingleObjectMixin
from users.models import Follow

from .forms import CommentForm, FollowForm, PostForm
from .mixins import (
    CacheMixin,
    IsAuthorAndLoginRequiredMixin,
    PostMixinListView,
    SearchMixin,
)
from .models import Comment, Post, ViewPost

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


class PostDetailView(View):
    """Класс представления определенного поста."""

    def get(self, request, *args, **kwargs):
        view = PostDetail.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = CommentCreateView.as_view()
        return view(request, *args, **kwargs)


class PostDetail(DetailView):
    """Класс представления определенного поста."""

    model = Post
    queryset = Post.objects.select_related("author", "group")
    template_name = "posts/post_detail.html"
    pk_url_kwarg = "post_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "form": CommentForm(self.request.POST or None),
                "form_follow": FollowForm(
                    initial={"author": self.object.author}
                ),
            }
        )
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(
            count_posts_of_author=Count("author__posts")
        )
        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                is_subscribed=Exists(
                    self.request.user.follower.filter(
                        author=OuterRef("author_id")
                    )
                )
            )
        comments = (
            Comment.objects.filter(post_id=self.kwargs.get("post_id"))
            .select_related("author")
            .order_by("-created")
        )
        queryset = queryset.prefetch_related(
            Prefetch("comments", queryset=comments)
        )
        return queryset

    def get_object(self, queryset=None):
        user = self.request.user
        obj = super().get_object()
        if user.is_authenticated and user != obj.author:
            ViewPost.objects.get_or_create(post=obj, user=self.request.user)
        return obj


class PostCreateView(LoginRequiredMixin, CreateView):
    """Класс представление для создания поста."""

    model = Post
    form_class = PostForm

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        form = self.get_form()
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        return super().form_valid(form)


class PostUpdateView(IsAuthorAndLoginRequiredMixin, UpdateView):
    """Класс представление для редактирования поста."""

    form_class = PostForm
    model = Post
    pk_url_kwarg = "post_id"

    def get_redirect_url(self):
        return self.get_object().get_absolute_url()


class PostDeleteView(IsAuthorAndLoginRequiredMixin, DeleteView):
    """Класс для удаления автором своего поста."""

    model = Post
    pk_url_kwarg = "post_id"
    success_url = reverse_lazy("posts:index")

    def get_redirect_url(self):
        return self.get_object().get_absolute_url()


class GroupPostListView(CacheMixin, PostMixinListView):
    """Класс представления списка постов по определенной группе."""

    def get_queryset(self):
        slug = self.kwargs.get("slug")
        queryset = super().get_queryset().filter(group__slug=slug)
        cache_name = f"posts_of_group_cache_{slug}"
        return self.get_cache(queryset, cache_name, self.cache_timeout)


class PostProfileListView(LoginRequiredMixin, ListView):
    """
    Класс представления личной страницы пользователя
    с отображением ленты его опубликованных постов.
    """

    template_name = "posts/post_of_user.html"
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
            User.objects.annotate(
                is_subscribed=Exists(
                    self.request.user.follower.filter(author=OuterRef("pk"))
                )
            ),
            username=username,
        )
        return self.author.posts.select_related("group")


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
        author_id = request.POST.get("author")
        author = get_object_or_404(User, pk=author_id)
        if author == request.user:
            messages.error(request, "Вы не можете подписать на самого себя.")
            return redirect(request.META.get("HTTP_REFERER", "/"))
        msg = f"Вы подписались на пользователя {author.username}"
        instance, created = Follow.objects.get_or_create(
            author=author, user=request.user
        )
        if not created:
            instance.delete()
            msg = "Подписка отменена."
        messages.success(request, msg)
        return redirect(request.META.get("HTTP_REFERER", "/"))


class CommentCreateView(LoginRequiredMixin, SingleObjectMixin, FormView):
    """Класс добавления нового комментария к определенному посту."""

    model = Post
    form_class = CommentForm
    template_name = "posts/post_detail.html"
    pk_url_kwarg = "post_id"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.post = self.object
        comment.author = self.request.user
        comment.save()
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return self.get_object().get_absolute_url() + "#comments"


class CommentDeleteView(IsAuthorAndLoginRequiredMixin, DeleteView):
    """Класс представления для удаления комментариев."""

    model = Comment

    def get_success_url(self) -> str:
        comment = self.get_object()
        return comment.post.get_absolute_url() + "#comments"

    def get_redirect_url(self):
        return self.get_object().post.get_absolute_url() + "#comments"


class CommentEditView(IsAuthorAndLoginRequiredMixin, UpdateView):
    """Класс представления для редактирования комментариев."""

    template_name = "posts/comment_edit.html"
    model = Comment
    form_class = CommentForm

    def get_success_url(self) -> str:
        comment = self.get_object()
        return comment.post.get_absolute_url() + "#comments"

    def get_redirect_url(self):
        return self.get_object().post.get_absolute_url() + "#comments"
