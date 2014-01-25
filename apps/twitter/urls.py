# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include
from views import DashboardView, CreateOrderWizard
from forms import OrderTypeForm, RelationshipForm

urlpatterns = patterns('',
                       url(r'^$', DashboardView.as_view(), name='twitter-home'),
                       url(r'^create-order/$', CreateOrderWizard.as_view([OrderTypeForm, RelationshipForm]),
                           name='twitter-create-order'),
)