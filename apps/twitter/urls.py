# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from views import DeleteScheduleOrderView, ScheduleOrderView, OrderView
from wizards import CreateOrderWizard, FORMS


urlpatterns = patterns('',
                       url(r'^$', ScheduleOrderView.as_view(), name='twitter-home'),
                       url(r'^order-history/$', OrderView.as_view(), name='twitter-order-history'),
                       url(r'^create-order/$', CreateOrderWizard.as_view(FORMS),
                           name='twitter-create-order'),
                       url(r'^delete/(?P<pk>[-\w]+)/$', DeleteScheduleOrderView.as_view(), name='twitter-delete'),
)