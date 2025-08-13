from django import template

import datetime

register = template.Library()


@register.filter(name='spanish_month')
def spanish_month(month_number: int):
    months = {
        1: "Enero",
        2: "Febrero",
        3: "Marzo",
        4: "Abril",
        5: "Mayo",
        6: "Junio",
        7: "Julio",
        8: "Agosto",
        9: "Setiembre",
        10: "Octubre",
        11: "Noviembre",
        12: "Diciembre"
    }
    return months[month_number]


@register.filter(name='spanish_day_of_the_week')
def spanish_day_of_the_week(day_number: int|datetime.datetime):
    if type(day_number) is not int:
        day_number = day_number.weekday()
    days = {
        0: "Lunes",
        1: "Martes",
        2: "Miércoles",
        3: "Jueves",
        4: "Viernes",
        5: "Sábado",
        6: "Domingo"
    }
    return days[day_number]


@register.filter(name='bootstrap_alert')
def bootstrap_alert(django_tag):
    if django_tag == "error":
        return "danger"
    return django_tag


@register.filter(name='urlencode')
def urlencode(url: str):
    from urllib.parse import quote
    return quote(url)
