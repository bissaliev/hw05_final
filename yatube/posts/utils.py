from django.contrib.postgres.search import (
    SearchHeadline,
    SearchQuery,
    SearchRank,
    SearchVector,
)
from django.core.cache import cache
from django.core.paginator import Paginator

from .models import Post

LIMIT_POSTS = 8


def get_page_context(queryset, request):
    """Паджинатор"""
    paginator = Paginator(queryset, LIMIT_POSTS)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return {
        "paginator": paginator,
        "page_number": page_number,
        "page_obj": page_obj,
    }


def q_search(query):
    """Полнотекстовый поиск постов по полям 'title' и 'text'."""
    vector = SearchVector("title", "text")
    query = SearchQuery(query)
    result = (
        Post.objects.annotate(rank=SearchRank(vector, query))
        .filter(rank__gt=0)
        .order_by("-rank")
    )
    result = result.annotate(
        headline=SearchHeadline(
            "title",
            query,
            start_sel='<span style="background-color: red;">',
            stop_sel="</span>",
        )
    )
    result = result.annotate(
        bodyline=SearchHeadline(
            "text",
            query,
            start_sel='<span style="background-color: red;">',
            stop_sel="</span>",
        )
    )
    return result


def get_client_ip(request):
    """
    Функция для определения IP-адреса пользователя.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    return (
        x_forwarded_for.split(",")[-1].strip()
        if x_forwarded_for
        else request.META.get("REMOTE_ADDR")
    )


def set_get_cache(query, cache_name, cache_time):
    """Функция для управлением кешированием."""
    data = cache.get(cache_name)
    if not data:
        data = query
        cache.set(cache_name, data, cache_time)
    return data


def cache_post_delete(post):
    """Функция для ивалидации кеша модели Post."""
    cache.delete("index_cache")
    follows = post.author.following.all()
    for follow in follows:
        cache.delete(f"post_follow_cache_{follow.user_id}")
