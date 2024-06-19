from django.conf import settings
from django.contrib.postgres.search import (
    SearchHeadline,
    SearchQuery,
    SearchRank,
    SearchVector,
)
from django.views.generic import ListView

from .models import Post


class PostMixinListView(ListView):
    """Класс-миксин представления списка постов."""

    template_name = "posts/index.html"
    queryset = Post.objects.select_related("author", "group").all()
    context_object_name = "posts"
    paginate_by = settings.PAGE_SIZE


class SearchMixin:
    """Класс-миксин для поиска постов."""

    def get_queryset(self):
        queryset = super().get_queryset()
        if query := self.request.GET.get("search", None):
            vector = SearchVector("title", "text")
            query = SearchQuery(query)
            queryset = (
                queryset.annotate(rank=SearchRank(vector, query))
                .filter(rank__gt=0)
                .order_by("-rank")
            )
            queryset = queryset.annotate(
                headline=SearchHeadline(
                    "title",
                    query,
                    start_sel='<span style="background-color: red;">',
                    stop_sel="</span>",
                )
            )
            queryset = queryset.annotate(
                bodyline=SearchHeadline(
                    "text",
                    query,
                    start_sel='<span style="background-color: red;">',
                    stop_sel="</span>",
                )
            )
            return queryset
        return queryset
