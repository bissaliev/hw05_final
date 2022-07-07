from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User
from .utils import get_page_context


@cache_page(20, key_prefix='index_page')
def index(request):
    """ Функция представления главной страницы."""
    posts_list = Post.objects.select_related('author', 'group').all()
    context = get_page_context(posts_list, request)
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """ Функция представления страницы группы."""
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.select_related('author', 'group').all()
    context = {
        'group': group,
    }
    context.update(get_page_context(posts_list, request))
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """ Функция представления страницы профиля автора."""
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    posts_count = posts.count()
    following = Follow.objects.filter(author=author).exists()
    context = {
        'author': author,
        'posts_count': posts_count,
        'following': following
    }
    context.update(get_page_context(posts, request))
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """ Функция представления страницы информации поста."""
    post = get_object_or_404(Post, pk=post_id)
    count_author = post.author.posts.count()
    comments = Comment.objects.select_related(
        'post',
    )
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'count_author': count_author,
        'form': form,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """ Функция представления страницы создания поста."""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('posts:profile', request.user.username)
    form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """ Функция представления страницы редактирования поста."""
    is_edit = True
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('posts:post_detail', post_id)
    form = PostForm(instance=post)
    return render(
        request, 'posts/create_post.html',
        {'form': form, 'is_edit': is_edit}
    )


@login_required
def add_comment(request, post_id):
    """ Функция добавления комментария."""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Функция представления постов избранных авторов."""
    user = request.user
    follows = user.follower
    author_ids = follows.values_list('author_id', flat=True)
    posts_list = Post.objects.filter(author_id__in=author_ids)
    context = get_page_context(posts_list, request)
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Функция подписки на автора."""
    user = request.user
    author = get_object_or_404(User, username=username)
    if user.follower.filter(author=author).exists() or user == author:
        return redirect('posts:profile', username=username)
    Follow.objects.create(user=user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Функция отписки от автора."""
    user = request.user
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=user, author=author).delete()
    return redirect('posts:profile', username=username)
