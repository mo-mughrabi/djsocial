# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from tasks import follow_back
from tasks import unfollow
from models import Twitter, ScheduleOrder


class DashboardView(View):
    """  """
    template_name = 'twitter/home.html'

    @method_decorator(login_required)
    def get(self, request):
        orders = ScheduleOrder.objects.filter(user=get_object_or_404(Twitter, user=request.user), run_once=False)
        return render(request, self.template_name, {'orders': orders})