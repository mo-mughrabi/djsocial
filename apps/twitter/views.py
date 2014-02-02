# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from models import Twitter, ScheduleOrder, Order
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage


class DashboardView(View):
    """  """
    template_name = 'twitter/home.html'

    @method_decorator(login_required)
    def get(self, request):
        scheduled_orders_list = ScheduleOrder.objects.filter(user=get_object_or_404(Twitter, user=request.user),
                                                        run_once=False)
        orders = Order.objects.filter(user=get_object_or_404(Twitter, user=request.user), ).order_by('-status')

        paginator = Paginator(scheduled_orders_list, 2)

        page = request.GET.get('page')
        try:
            scheduled_orders = paginator.page(page)
        except PageNotAnInteger:
            scheduled_orders = paginator.page(1)
        except EmptyPage:
            scheduled_orders = paginator.page(paginator.num_pages)

        return render(request, self.template_name, {'scheduled_orders': scheduled_orders, 'orders': orders})