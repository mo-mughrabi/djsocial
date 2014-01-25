# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.template import RequestContext
from apps.twitter.forms import OrderTypeForm, RelationshipForm, AutoTweetForm
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.formtools.wizard.views import SessionWizardView
from apps.twitter.models import Twitter

FORMS = [("order_step", OrderTypeForm),
         ("relationship_step", RelationshipForm),
         ("auto_tweet_step", AutoTweetForm)]


def toggle_relationship_form(wizard):
    """Return true if user selected (follow or unfollow order type)"""
    # Get cleaned data from payment step
    cleaned_data = wizard.get_cleaned_data_for_step('order_step') or {'order_type': 'none'}
    # Return true
    return cleaned_data['order_type'] in ('follow_form', 'unfollow_form')


def toggle_auto_tweet_form(wizard):
    """Return true if user selected auto re-tweet"""
    # Get cleaned data from payment step
    cleaned_data = wizard.get_cleaned_data_for_step('order_step') or {'order_type': 'none'}
    # Return true
    return cleaned_data['order_type'] in ('retweet_form', 'favorite_form')


class CreateOrderWizard(SessionWizardView):
    """ CreateOrderWizard
    """
    file_storage = FileSystemStorage(location=os.path.join(getattr(settings, 'MEDIA_ROOT'), 'wizard'))
    condition_dict = {'relationship_step': toggle_relationship_form, 'auto_tweet_step': toggle_auto_tweet_form}
    base_wizard = 'twitter/wizard/'

    def __init__(self, *args, **kwargs):
        super(CreateOrderWizard, self).__init__(*args, **kwargs)

    def get_template_names(self):
        return ['{0}steps.html'.format(self.base_wizard)]

    def get_form_initial(self, step):

        if step in ('relationship_step', 'auto_tweet_step'):
            cleaned_data = self.get_cleaned_data_for_step('order_step')
            init_dict = {}

            if cleaned_data.get('order_type'):
                init_dict.update({'operation': cleaned_data.get('order_type').replace('_form', '')})
                return init_dict

        return self.initial_dict.get(step, {})

    def get_form_kwargs(self, step):
        return {'user': self.request.user}

    def done(self, form_list, **kwargs):
        for form in form_list:
            if isinstance(form, AutoTweetForm) or isinstance(form, RelationshipForm):
                obj = form.save(commit=False)
                obj.user = get_object_or_404(Twitter, user=self.request.user)
                obj.save()
        return render_to_response('twitter/wizard/done.html', {
            'form_data': [form.cleaned_data for form in form_list],
        }, context_instance=RequestContext(self.request))