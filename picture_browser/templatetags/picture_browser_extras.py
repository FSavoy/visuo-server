from django import template
from django.template.defaultfilters import stringfilter
from fractions import Fraction

"""
Custom filter for the picture browsing page template
"""

register = template.Library()

@register.filter
@stringfilter
def thumbnail(value, size):
    """
    Get the thumbnail of 'size' of the corresponding url
    """

    return value.replace('.jpg', '.' + size + '.jpg')

@register.filter
@stringfilter
def aperture(value):
    """
    Formats the value to display aperture as f/X
    """

    return 'f/'+value

@register.filter
@stringfilter
def exposure(value):
    """
    Formats the value to display exposure as a fraction
    """

    return str(Fraction(value).limit_denominator(4000))
