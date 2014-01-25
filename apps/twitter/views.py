# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from tasks import follow_back
from tasks import unfollow
from models import Twitter
from django.shortcuts import render_to_response
from django.contrib.formtools.wizard.views import SessionWizardView


class DashboardView(View):
    """  """
    template_name = 'twitter/home.html'

    @method_decorator(login_required)
    def get(self, request):

        return render(request, self.template_name, {})

    @method_decorator(login_required)
    def post(self, request):
        account = Twitter.objects.get(user=request.user)
        if request.POST['form-type'] == u'Follow back':
            follow_back.delay(account.id, )
        else:
            unfollow.delay(account.id, )
        return render(request, self.template_name, {})


class CreateOrderWizard(SessionWizardView):
    """ CreateOrderWizard
    """
    base_wizard = 'twitter/wizard/'

    def done(self, form_list, **kwargs):
        return render_to_response('twitter/wizard/done.html', {
            'form_data': [form.cleaned_data for form in form_list],
        }, context_instance=RequestContext(self.request))

    def get_template_names(self):
        return ['{0}steps.html'.format(self.base_wizard)]

    def get_form_initial(self, step):

        if step == u'1':
            cleaned_data = self.get_cleaned_data_for_step(u'0')
            init_dict = {}

            if cleaned_data.get('order_type') in (u'follow_form', u'unfollow_form'):
                init_dict.update({'operation': cleaned_data.get('order_type').replace('_form', '')})
                return init_dict

        return self.initial_dict.get(step, {})
