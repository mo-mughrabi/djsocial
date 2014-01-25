# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from django.utils.translation import ugettext_lazy as _


class OrderTypeForm(forms.Form):
    """ OrderTypeForm
    """
    order_types = (
        ('follow_form', _('Auto follow back')),
        ('unfollow_form', _('Auto unfollow back')),
        ('retweet_form', _('Auto retweet')),
        ('FavForm', _('Auto favirote')),
    )
    order_type = forms.ChoiceField(choices=order_types, widget=forms.Select(attrs={'class': 'form-control'}))


class RelationshipForm(forms.Form):
    """ RelationshipForm
    """
    operation_options = (
        ('follow', _('Follow')),
        ('unfollow', _('Unfollow')),
    )
    execution_options = (
        ('once', _('Execute once')),
        ('daily', _('Schedule daily')),
    )
    operation = forms.ChoiceField(choices=operation_options)
    execution = forms.ChoiceField(choices=execution_options, widget=forms.Select(attrs={'class': 'form-control'}))
    exclude = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
                              help_text=_('Use comma seperated usernames that you want to exclude'), required=False)


class AutoRetweetForm(forms.Form):
    """ AutoRetweetForm
    """
    execution_options = (
        ('once', _('Execute once')),
        ('daily', _('Schedule daily')),
    )
    search_style_options = (
        (0, 'Search once a day, re-tweet result every hour'),
        (0, 'Search every hour, re-tweet result'),
    )
    maximum_per_hour_options = (
        (.0, '2 per hour'),
        (1, '1 per hour'),
        (2, '1 every two hours'),
        (4, '1 every 4 hours'),
    )
    execution = forms.ChoiceField(choices=execution_options, widget=forms.Select(attrs={'class': 'form-control'}))
    search_by_hash_tag = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), help_text=_(
        'Hash Tag will be used to search for tweets desired for retweeting'))
    search_style = forms.ChoiceField(choices=search_style_options, widget=forms.Select(attrs={'class': 'form-control'}))
    maximum_per_hour = forms.ChoiceField(choices=maximum_per_hour_options, label=_('Maximum re-tweets per hour'),
                                                widget=forms.Select(attrs={'class': 'form-control'}))