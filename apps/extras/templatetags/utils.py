# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import template
from django.core.urlresolvers import reverse

register = template.Library()


@register.simple_tag
def dict_key_lookup(the_dict, key):
    # Try to fetch from the dict, and if it's not found return an empty string.
    return the_dict.get(key, '')

@register.filter
def is_active(request, url):
    """ """
    if request.path == reverse(url):
        return True
    else:
        return False