# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.template import RequestContext
from apps.twitter.forms import OrderTypeForm, RelationshipForm, AutoRetweetForm
from django.shortcuts import render_to_response
from django.contrib.formtools.wizard.views import SessionWizardView

FORMS = [("order_step", OrderTypeForm),
         ("relationship_step", RelationshipForm),
         ("retweet_step", AutoRetweetForm)]


def toggle_relationship_form(wizard):
    """Return true if user selected (follow or unfollow order type)"""
    # Get cleaned data from payment step
    cleaned_data = wizard.get_cleaned_data_for_step('order_step') or {'order_type': 'none'}
    # Return true
    return cleaned_data['order_type'] in ('follow_form', 'unfollow_form')


def toggle_retweet_form(wizard):
    """Return true if user selected auto re-tweet"""
    # Get cleaned data from payment step
    cleaned_data = wizard.get_cleaned_data_for_step('order_step') or {'order_type': 'none'}
    # Return true
    return cleaned_data['order_type'] in 'retweet_form'


class CreateOrderWizard(SessionWizardView):
    """ CreateOrderWizard
    """
    file_storage = FileSystemStorage(location=os.path.join(getattr(settings, 'MEDIA_ROOT'), 'wizard'))
    condition_dict = {'relationship_step': toggle_relationship_form}
    base_wizard = 'twitter/wizard/'

    def __init__(self, *args, **kwargs):
        super(CreateOrderWizard, self).__init__(*args, **kwargs)

    def get_template_names(self):
        return ['{0}steps.html'.format(self.base_wizard)]

    def get_form_initial(self, step):

        if step in ('relationship_step', ):
            cleaned_data = self.get_cleaned_data_for_step('order_step')
            init_dict = {}

            if cleaned_data.get('order_type') in (u'follow_form', u'unfollow_form'):
                init_dict.update({'operation': cleaned_data.get('order_type').replace('_form', '')})
                return init_dict

        return self.initial_dict.get(step, {})

    def done(self, form_list, **kwargs):
        return render_to_response('twitter/wizard/done.html', {
            'form_data': [form.cleaned_data for form in form_list],
        }, context_instance=RequestContext(self.request))