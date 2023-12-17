# your_app/templatetags/custom_filters.py

from django import template
import re

register = template.Library()

@register.filter
def remove_images(value):
    # Regularni izraz za uklanjanje img tagova
    return re.sub(r'<img .*?>', '', value)
