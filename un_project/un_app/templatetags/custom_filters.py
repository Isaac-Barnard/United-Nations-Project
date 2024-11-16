from django import template
from decimal import Decimal

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


@register.filter
def subtract(value, arg):
    """Subtract one decimal from another"""
    try:
        return Decimal(str(value)) - Decimal(str(arg))
    except:
        return Decimal('0')

@register.filter
def sum_attribute(queryset, attribute):
    """Sum a specific attribute across a queryset"""
    try:
        return sum(getattr(obj, attribute) or Decimal('0') for obj in queryset)
    except:
        return Decimal('0')

@register.filter
def sum_paid_amounts(queryset):
    """Calculate total paid amounts for a queryset of liabilities"""
    try:
        return sum((obj.total_diamond_value - obj.remaining_diamond_value) for obj in queryset)
    except:
        return Decimal('0')