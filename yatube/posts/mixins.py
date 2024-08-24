from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.postgres.search import (
    SearchHeadline,
    SearchQuery,
    SearchRank,
)
from django.core.cache import cache
from django.db.models import QuerySet
from django.shortcuts import redirect
from django.views.generic import ListView

from .models import Post


class PostMixinListView(ListView):
    """Класс-миксин представления списка постов."""

    template_name = "posts/index.html"
    queryset = (
        Post.objects.defer(
            "search_vector",
            "author__password",
            "author__is_superuser",
            "author__email",
            "author__is_staff",
            "author__is_active",
            "author__date_joined",
            "author__last_login",
            "author__birth_date",
            "group__description",
        )
        .select_related("author", "group")
        .all()
    )
    context_object_name = "posts"
    paginate_by = settings.PAGE_SIZE


class SearchMixin:
    """Класс-миксин для поиска постов."""

    def get_queryset(self):
        queryset = super().get_queryset()
        if query := self.request.GET.get("search", None):
            query = SearchQuery(query, config="russian")
            queryset = (
                queryset.annotate(rank=SearchRank("search_vector", query))
                .filter(search_vector=query, rank__gt=0)
                .order_by("-rank")
            )
            queryset = queryset.annotate(
                headline=SearchHeadline(
                    "title",
                    query,
                    start_sel='<span style="background-color: red;">',
                    stop_sel="</span>",
                    config="russian",
                )
            )
            queryset = queryset.annotate(
                bodyline=SearchHeadline(
                    "text",
                    query,
                    start_sel='<span style="background-color: red;">',
                    stop_sel="</span>",
                    config="russian",
                )
            )
            return queryset
        return queryset


class CacheMixin:
    """
    Миксин для управление кешированием.
    """

    cache_timeout = 900

    def get_cache(self, query: QuerySet, cache_name: str, cache_timeout: int):
        data = cache.get(cache_name)
        if not data:
            data = query
            cache.set(cache_name, query, cache_timeout)
        return data


class IsAuthorAndLoginRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return self.handle_no_permission()
        obj = self.get_object()
        if request.user != obj.author:
            messages.error(
                request, "У вас нет прав на изменение чужой записи."
            )
            return redirect(self.get_redirect_url())
        return super().dispatch(request, *args, **kwargs)

    def get_redirect_url(self):
        pass
