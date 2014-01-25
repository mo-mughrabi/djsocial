# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from tasks import follow_back
from tasks import unfollow
from models import Twitter


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