# -*- coding: utf-8 -*-
from django import template

"""
Custom filters for the visualization page template to format data with their respective units
"""

register = template.Library()

@register.filter
def temperature(value):
    return "%.2f" % value + " °C"

@register.filter
def dew_pt(value):
    return "%.2f" % value+" °C"

@register.filter
def wind_speed(value):
    return "%.2f" % value + " km/h"

@register.filter
def pressure(value):
    return "%.2f" % value + " hPa"

@register.filter
def rain(value):
    return  "%.2f" % value + " mm"

@register.filter
def cloud_height(value):
    return  "%.2f" % value + " m"

@register.filter
def formatDate(value):
    return  value.strftime("%d-%m-%Y")

@register.filter
def formatTime(value):
    return  value.strftime("%H:%M:%S")