# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from djorm_hstore.models import HStoreManager


class TwitterManager(models.Manager):
    """ TwitterManager """


class ScheduleOrderManger(HStoreManager):
    """ ScheduleOrder """


class OrderManager(HStoreManager):
    """
    """