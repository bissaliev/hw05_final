from django import template
from django.utils import timezone
from posts.models import Group
from posts.utils import set_get_cache

register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={"class": css})


@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    """
    Функция для исправления совместимости фильтра и паджинатора;
    Извлекает из kwargs номера страниц и добавляет их в контекст
    параллельно удаляя старые данные.
    """

    d = context["request"].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    for k in [k for k, v in d.items() if not v]:
        del d[k]
    return d.urlencode()


@register.filter
def time_since_post(created_at):
    now = timezone.now()
    diff = now - created_at

    if diff.days == 0 and diff.seconds < 60:
        return "Только что"
    if diff.days == 0 and diff.seconds < 3600:
        minutes = diff.seconds // 60
        return f"{minutes} минут назад"
    if diff.days == 0:
        hours = diff.seconds // 3600
        return f"{hours} часов назад"
    if diff.days < 30:
        return f"{diff.days} дней назад"
    if diff.days < 365:
        months = diff.days // 30
        return f"{months} месяцев назад"
    years = diff.days // 365
    return f"{years} лет назад"


@register.inclusion_tag("tags/group_list.html", takes_context=True)
def get_post_of_group(context):
    query = Group.objects.all()
    path = context.request.path.strip("/").split("/")
    current_group = None
    if path[0] == "group":
        current_group = path[-1]
    return {
        "group_list": set_get_cache(query, "post_of_group_tag", 900),
        "current_group": current_group,
    }
