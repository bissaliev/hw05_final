from django.contrib.postgres.search import (
    SearchHeadline,
    SearchQuery,
    SearchRank,
    SearchVector,
)
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
