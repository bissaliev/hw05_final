from django import template


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
