# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.core import management
import os
from django.conf import settings
import tweepy
from tweepy import Stream
from tweepy import OAuthHandler, Cursor
from tweepy.streaming import StreamListener
from apps.twitter.models import Twitter


def get_diff(list1, list2):
    """Outputs objects which are in list1 but not list 2"""
    return list(set(list1).difference(set(list2)))


class Command(BaseCommand):
    args = '<No arguments>'

    def handle(self, *args, **options):
        auth = OAuthHandler(getattr(settings, 'TWITTER_CONSUMER_KEY'), getattr(settings, 'TWITTER_CONSUMER_SECRET'))
        account = Twitter.objects.get(pk=1)
        auth.set_access_token(account.access_token, account.secret_key)
        api = tweepy.API(auth)

        last_id = None

        for tweet in Cursor(api.user_timeline, screen_name='bebeknil1', include_rts=False).items(10):
            if last_id is None:
                last_id = tweet.id
            print tweet.text, tweet.id

        print '----- new query'
        for tweet in Cursor(api.user_timeline, screen_name='bebeknil1', since_id=last_id, include_rts=False).items():
            print tweet.text, tweet.id
            last_id = tweet.id
            print

        print last_id
