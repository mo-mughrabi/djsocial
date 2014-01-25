# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from models import ScheduleOrder, Twitter


class OrderTypeForm(forms.Form):
    """ OrderTypeForm
    """
    order_types = (
        ('follow_form', _('Auto follow back')),
        ('unfollow_form', _('Auto unfollow back')),
        ('retweet_form', _('Auto retweet')),
        ('favorite_form', _('Auto favirote')),
    )
    order_type = forms.ChoiceField(choices=order_types, widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('user') or None
        kwargs.pop('user')
        super(OrderTypeForm, self).__init__(*args, **kwargs)


class RelationshipForm(forms.ModelForm):
    """ RelationshipForm
    """
    operation_options = (
        ('follow', _('Follow')),
        ('unfollow', _('Unfollow')),
    )
    execution_options = (
        (True, _('Execute once')),
        (False, _('Schedule daily')),
    )
    operation = forms.ChoiceField(choices=operation_options, widget=forms.HiddenInput)
    execution = forms.ChoiceField(choices=execution_options, widget=forms.Select(attrs={'class': 'form-control'}))
    exclude = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
                              help_text=_('Use comma separated username that you want to exclude'), required=False)

    class Meta:
        model = ScheduleOrder
        fields = ('operation', 'execution', 'exclude')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('user') or None
        kwargs.pop('user')
        super(RelationshipForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        obj = super(RelationshipForm, self).save(commit=commit)

        obj.label = '{0} back: runs {1}'.format(cleaned_data.get('operation'),
                                                'once' if cleaned_data.get('execution') == u'True' else 'daily')
        obj.run_once = True if cleaned_data.get('execution') == u'True' else False
        obj.func = cleaned_data.get('operation')
        obj.kwargs = {'exclude': cleaned_data.get('exclude') or ''}
        return obj

    def clean(self):
        cleaned_data = self.cleaned_data
        try:
            label = '{0} back: runs {1}'.format(cleaned_data.get('operation'),
                                                'once' if cleaned_data.get('execution') == u'True' else 'daily')
            obj = ScheduleOrder.objects.get(label=label, user=get_object_or_404(Twitter, user=self.user), run_once=False)
            raise forms.ValidationError(_('This is a duplicate setup, you already have "{}"'.format(obj.label)))
        except ScheduleOrder.DoesNotExist:
            pass
        return cleaned_data


class AutoTweetForm(forms.Form):
    """ AutoTweetForm
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

    search_by_hash_tag = forms.SlugField(widget=forms.TextInput(attrs={'class': 'form-control'}), help_text=_(
        'Hash Tag will be used to search for tweets desired for retweeting'))

    search_style = forms.ChoiceField(choices=search_style_options, widget=forms.Select(attrs={'class': 'form-control'}))

    maximum_per_hour = forms.ChoiceField(choices=maximum_per_hour_options, label=_('Maximum re-tweets per hour'),
                                         widget=forms.Select(attrs={'class': 'form-control'}))

    minimum_favorite = forms.DecimalField(initial=0, widget=forms.TextInput(
        attrs={'class': 'form-control', 'data-group-class': 'col-xs-3'}), )

    minimum_retweet = forms.DecimalField(initial=0, widget=forms.TextInput(
        attrs={'class': 'form-control', 'data-group-class': 'col-xs-3'}), )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('user') or None
        kwargs.pop('user')
        super(AutoTweetForm, self).__init__(*args, **kwargs)