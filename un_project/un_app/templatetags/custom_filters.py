from django import template

register = template.Library()

@register.filter
def custom_decimal_places(value):
    if value is None:
        return ''
    if value == 0:
        return '0'
    return f"{value:.3f}" if value % 1 != 0 else f"{value:.1f}"


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)