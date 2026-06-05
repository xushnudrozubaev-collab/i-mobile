from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()


@register.filter(name='money')
def money(value):
    """
    Sonni bo'shliq bilan ajratib chiqaradi.
    Misol: 14400500 → "14 400 500"
    Oxiriga " сўм" qo'shilmaydi — shablonda yoziladi.
    """
    try:
        value = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return value

    # Butun va kasr qismlarni ajratish
    int_part = int(value)
    # Manfiy sonlar uchun
    sign = '-' if int_part < 0 else ''
    abs_int = abs(int_part)

    # 3 xonali guruhlarga bo'lish (bo'shliq bilan)
    formatted = '{:,}'.format(abs_int).replace(',', '\u00a0')  # non-breaking space
    return f"{sign}{formatted}"


@register.filter(name='summa')
def summa(value):
    """money + ' сўм' """
    return f"{money(value)} сўм"
