# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.conf import settings
import tweepy
from tweepy import OAuthHandler, Cursor
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
        i = 0
        x = None
        for tweet in Cursor(api.search, q='kuwait', result_type='popular', since_id='').items():
            i = i +1
            print tweet.id, tweet.author.screen_name
            print i
            print '+++++++++++++'
        # for tweet in api.search(q='shemale', result_type='mixed', since_id='428429007902998528', count='100'):
        #     print '--- new tweet ---'
        #     print tweet.text
        #     print tweet.id
        #     print tweet.author.screen_name

        # for tweet in Cursor(api.user_timeline, screen_name='xxx', include_rts=False).items(10):
        #     if last_id is None:
        #         last_id = tweet.id
        #     #print tweet.author.screen_name
        #     print tweet.__dict__
        #
        # print '----- new query'
        # for tweet in Cursor(api.user_timeline, screen_name='xxx', since_id=last_id, include_rts=False).items():
        #     print tweet.text, tweet.id
        #     last_id = tweet.id
        #     print

        print last_id
