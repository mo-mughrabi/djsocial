# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from djorm_hstore.fields import DictionaryField
from djorm_pgarray.fields import ArrayField
from jsonfield import JSONField
from tweepy import OAuthHandler
import tweepy
from managers import TwitterManager, ScheduleOrderManger


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
    FUNCTIONS = (
        ('follow_user', 'Follow user'),
        ('unfollow_user', 'Unfollow user'),
        ('retweet', 'Retweet'),
        ('favourite', 'Favourite'),
    )
    status_options = (
        ('A', 'Active'),
        ('D', 'Deleted'),
        ('R', 'Running'),
    )

    user = models.ForeignKey(Twitter)
    label = models.CharField(_('Label'), max_length=250)
    run_once = models.BooleanField(default=True)
    status = models.CharField(max_length=6, choices=status_options, default='A')
    func = models.CharField(max_length=200, choices=FUNCTIONS)
    args = ArrayField(dbtype="text")
    kwargs = DictionaryField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_run = models.DateTimeField(null=True, blank=True)

    objects = ScheduleOrderManger()

    def __unicode__(self):
        return u'%s' % self.label


class Order(models.Model):
    """ Order
    """
    PENDING = 'E'
    COMPLETED = 'C'
    FAILED = 'F'
    STATUSES = (
        (PENDING, 'Pending'),
        (FAILED, 'Failed'),
        (COMPLETED, 'Completed'),
    )
    FUNCTIONS = (
        ('follow_user', 'Follow user'),
        ('unfollow_user', 'Unfollow user'),
        ('retweet', 'Retweet'),
        ('favourite', 'Favourite'),
    )
    user = models.ForeignKey(Twitter)
    parent = models.ForeignKey('self', null=True, blank=True)
    schedule_order = models.ForeignKey(ScheduleOrder, null=True, blank=True)
    perform_at = models.DateTimeField(auto_now_add=True)
    performed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=2, choices=STATUSES)
    func = models.CharField(max_length=200, choices=FUNCTIONS)
    args = models.CharField(max_length=100)
    kwargs = JSONField(null=True, blank=True)
    result = models.TextField(null=True, blank=True)

    def run_order(self):
        # execute operation based on type and args
        auth = OAuthHandler(getattr(settings, 'TWITTER_CONSUMER_KEY'), getattr(settings, 'TWITTER_CONSUMER_SECRET'))
        auth.set_access_token(self.user.access_token, self.user.secret_key)
        api = tweepy.API(auth)

        try:
            args = self.args.split(',')
        except:
            # handle if args is a single argument or none
            raise
        if self.func == 'follow_user':
            api.create_friendship(args[0])
        if self.func == 'unfollow_user':
            api.destroy_friendship(args[0])
        if self.func == 'retweet':
            api.retweet(args[0])
        if self.func == 'favourite':
            api.create_favorite(args[0])

