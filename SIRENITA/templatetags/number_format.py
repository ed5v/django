from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter
def format_number_en(value):
    """Format decimal values as 1,234.56 regardless of locale."""
    if value in (None, ""):
        return "0.00"
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return value
    return f"{amount:,.2f}"


@register.filter
def format_int_en(value):
    """Format integers as 1,234 regardless of locale."""
    if value in (None, ""):
        return "0"
    try:
        number = int(value)
    except (TypeError, ValueError):
        return value
    return f"{number:,}"
