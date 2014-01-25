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
        ('RetweetForm', _('Auto retweet')),
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
    operation = forms.ChoiceField(choices=operation_options, widget=forms.HiddenInput())
    execution = forms.ChoiceField(choices=execution_options, widget=forms.Select(attrs={'class': 'form-control'}))
    exclude = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
                              help_text=_('Use comma seperated usernames that you want to exclude'), required=False)

