# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.views.generic.base import View


class Home(View):
    """  """
    template_name = 'pages/home.html'

    def get(self, request):
        return render(request, self.template_name, {})


