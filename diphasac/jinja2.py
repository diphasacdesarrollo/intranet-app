from django.templatetags.static import static
from django.urls import reverse
from django.utils.timezone import template_localtime

from jinja2 import Environment
from main.templatetags import main_extras


def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'static': static,
        'url': reverse,
        'localtime': template_localtime,
    })
    env.filters.update({
        'bootstrap_alert': main_extras.bootstrap_alert,
        'localtime': template_localtime,
        'spanish_month': main_extras.spanish_month,
        'spanish_day_of_the_week': main_extras.spanish_day_of_the_week,
        'urlencode': main_extras.urlencode,
    })
    return env
