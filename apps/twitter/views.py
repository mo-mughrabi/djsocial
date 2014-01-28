# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from models import Twitter, ScheduleOrder


class DashboardView(View):
    """  """
    template_name = 'twitter/home.html'

    @method_decorator(login_required)
    def get(self, request):
        scheduled_orders = ScheduleOrder.objects.filter(user=get_object_or_404(Twitter, user=request.user),
                                                        run_once=False)
        orders = ScheduleOrder.objects.filter(user=get_object_or_404(Twitter, user=request.user), run_once=True)
        return render(request, self.template_name, {'scheduled_orders': scheduled_orders, 'orders': orders})