from django.core.paginator import Paginator

LIMIT_POSTS = 10


def get_page_context(queryset, request):
    """ Паджинатор"""
    paginator = Paginator(queryset, LIMIT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'paginator': paginator,
        'page_number': page_number,
        'page_obj': page_obj,
    }
