# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.template.defaultfilters import truncatechars
from django.utils.translation import ugettext_lazy as _
from djorm_hstore.fields import DictionaryField
from djorm_pgarray.fields import ArrayField

from managers import TwitterManager, ScheduleOrderManger, OrderManager


class Twitter(models.Model):
    """
    """
    user = models.ForeignKey(getattr(settings, 'AUTH_USER_MODEL'))
    tid = models.CharField(_('Twitter ID'), max_length=200)
    screen_name = models.CharField(_('Screen name'), max_length=200)
    access_token = models.CharField(_('Access token'), max_length=200)
    secret_key = models.CharField(_('Secret Key'), max_length=200)
    followers_sum = models.PositiveIntegerField(default=0)
    following_sum = models.PositiveIntegerField(default=0)

    objects = TwitterManager()

    def __unicode__(self):
        return u'%s' % self.user


class ScheduleOrder(models.Model):
    """ ScheduleOrder
    """
    function_options = (
        ('follow_user', 'Follow user'),
        ('unfollow_user', 'Unfollow user'),
        ('retweet', 'Retweet'),
        ('favourite', 'Favourite'),
    )
    status_options = (
        ('A', 'Active'),
        ('D', 'Deleted'),
        ('R', 'Running'),
        ('P', 'Pending'),
    )

    user = models.ForeignKey(Twitter)
    label = models.CharField(_('Label'), max_length=250)
    run_once = models.BooleanField(default=True)
    status = models.CharField(max_length=6, choices=status_options, default='A')
    func = models.CharField(max_length=200, choices=function_options)
    args = ArrayField(dbtype='text', null=True, blank=True)
    kwargs = DictionaryField(null=True, blank=True, db_index=True)
    data = DictionaryField(null=True, blank=True, help_text=_('Used to maintain data about process details'))
    created_at = models.DateTimeField(auto_now_add=True)
    last_run = models.DateTimeField(null=True, blank=True)

    objects = ScheduleOrderManger()

    def __unicode__(self):
        return u'%s' % self.label

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.run_once and self.status == 'A':
            self.status = 'P'

        super(ScheduleOrder, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                        update_fields=update_fields)


class Order(models.Model):
    """ Order
    """
    PENDING = 'P'
    COMPLETED = 'C'
    FAILED = 'F'
    status_options = (
        (PENDING, 'Pending'),
        (FAILED, 'Failed'),
        (COMPLETED, 'Completed'),
    )
    function_options = (
        ('follow_user', 'Follow user'),
        ('unfollow_user', 'Unfollow user'),
        ('retweet', 'Retweet'),
        ('favourite', 'Favourite'),
    )
    user = models.ForeignKey(Twitter)
    schedule_order = models.ForeignKey(ScheduleOrder, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    executed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=2, choices=status_options, default=PENDING)
    func = models.CharField(max_length=200, )
    args = ArrayField(dbtype='text', null=True, blank=True)
    kwargs = DictionaryField(null=True, blank=True, db_index=True)
    result = models.TextField(null=True, blank=True)

    objects = OrderManager()

    def __unicode__(self):

        try:
            return u'{0} "{1}" by {2}'.format(self.kwargs['func'].capitalize(), truncatechars(self.kwargs['tweet'], 50),
                                              self.kwargs['screen_name'])
        except KeyError:
            return u'%s' % self.func

    @property
    def kwargs_tweet(self):
        try:
            return self.kwargs['tweet']
        except:
            return None

    @property
    def kwargs_screen_name(self):
        try:
            return self.kwargs['screen_name']
        except:
            return None