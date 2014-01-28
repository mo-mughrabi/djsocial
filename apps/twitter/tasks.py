# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from celery import task
from celery.schedules import crontab
from celery.task import periodic_task
import datetime
from django.conf import settings
from celery.utils.log import get_task_logger
from django.db.models import Q, Count, Max
from pytz import utc
from apps.twitter.models import Order, ScheduleOrder
import tweepy
from tweepy import OAuthHandler, Cursor
from models import Twitter
import time

# setup logger
logger = get_task_logger(__name__)


@periodic_task(run_every=crontab(minute="*/1"))
def process_scheduled_orders():
    """ process_scheduled_orders """
    logger.debug('process_scheduled_orders is starting up')
    delta_time = datetime.datetime.utcnow().replace(tzinfo=utc) - datetime.timedelta(hours=1)
    auth = OAuthHandler(getattr(settings, 'TWITTER_CONSUMER_KEY'), getattr(settings, 'TWITTER_CONSUMER_SECRET'))

    for order in ScheduleOrder.objects.filter(
                    Q(Q(last_run__lte=delta_time) | Q(last_run__isnull=True)) & Q(run_once=False)):
        logger.debug('Order details: {}'.format(order.id))
        auth.set_access_token(order.user.access_token, order.user.secret_key)
        api = tweepy.API(auth)

        if order.func in ('retweet_watch', 'favorite_watch'):
            # if user is first timer
            if order.last_run is None:
                for user in order.args:
                    last_id = None
                    for tweet in Cursor(api.user_timeline, screen_name=user, include_rts=False).items(5):
                        if last_id is None:
                            last_id = tweet.id
                        Order.objects.create(user=order.user, func=order.kwargs['func'], args=[tweet.id, ],
                                             schedule_order=order,
                                             kwargs={
                                                 'func': order.kwargs['func'],
                                                 'tweet': tweet.text,
                                                 'tweet_id': tweet.id,
                                                 'source_url': tweet.source_url,
                                                 'created_at': tweet.created_at,
                                                 'screen_name': tweet.author.screen_name})
                    order.data[user] = last_id
                    order.last_run = datetime.datetime.utcnow().replace(tzinfo=utc)
                    order.save()
            else:
                # the hourly runs
                for user in order.args:
                    last_id = None
                    for tweet in Cursor(api.user_timeline, screen_name=user, include_rts=False,
                                        since_id=order.data[user]).items():
                        if last_id is None:
                            last_id = tweet.id
                        Order.objects.create(user=order.user, func=order.kwargs['func'], args=[tweet.id, ],
                                             schedule_order=order,
                                             kwargs={
                                                 'func': order.kwargs['func'],
                                                 'tweet': tweet.text,
                                                 'tweet_id': tweet.id,
                                                 'source_url': tweet.source_url,
                                                 'created_at': tweet.created_at,
                                                 'screen_name': tweet.author.screen_name})
                    order.data[user] = last_id or order.data[user]
                    order.last_run = datetime.datetime.utcnow().replace(tzinfo=utc)
                    order.save()

    logger.info('process_scheduled_orders ended successfully')
    return u'Success'


@periodic_task(run_every=crontab(minute="*/1"))
def provision_orders():
    """ provision_orders """
    logger.debug('provision_orders is starting up')
    delta_time = datetime.datetime.utcnow().replace(tzinfo=utc) - datetime.timedelta(hours=1)
    auth = OAuthHandler(getattr(settings, 'TWITTER_CONSUMER_KEY'), getattr(settings, 'TWITTER_CONSUMER_SECRET'))

    threshold = 24  # per hour

    for pending in Order.objects.values('user').filter(status=Order.PENDING).annotate(Count('user')):
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        hour_usage = Order.objects.filter(executed_at__year=now.year, executed_at__month=now.month,
                                          executed_at__day=now.day, executed_at__hour=now.hour,
                                          status__in=(Order.COMPLETED, Order.FAILED),
                                          user_id=pending.get('user'))
        logger.debug(hour_usage.query())
        hour_usage = hour_usage.count()
        logger.debug('provision_orders: user hourly usage: {}'.format(hour_usage))
        # skip user as he/she reached limit of hourly usage
        if hour_usage > 5:
            continue
        for order in Order.objects.filter(status=Order.PENDING, user_id=pending.get('user')):
            order.status = order.COMPLETED
            order.executed_at = datetime.datetime.utcnow().replace(tzinfo=utc)
            order.save()

    logger.info('provision_orders ended successfully')
    return u'Success'

#
# @task()
# def follow_back(account_id):
#     auth = OAuthHandler(getattr(settings, 'TWITTER_CONSUMER_KEY'), getattr(settings, 'TWITTER_CONSUMER_SECRET'))
#     account = Twitter.objects.get(pk=account_id)
#     auth.set_access_token(account.access_token, account.secret_key)
#     api = tweepy.API(auth)
#     #user = api.me()
#
#     follower_ids = []
#     for follower in tweepy.Cursor(api.followers).items():
#         follower_ids.append(follower.id)
#
#     friend_ids = []
#     for friend in tweepy.Cursor(api.friends).items():
#         friend_ids.append(friend.id)
#
#     follow_list = get_diff(follower_ids, friend_ids)
#
#     for follower in follow_list:
#         Order.objects.create(user=account, func='follow_user', args='{},'.format(follower))
#     return u'Success'

#
# @task()
# def unfollow(account_id):
#     auth = OAuthHandler(getattr(settings, 'TWITTER_CONSUMER_KEY'), getattr(settings, 'TWITTER_CONSUMER_SECRET'))
#     account = Twitter.objects.get(pk=account_id)
#     auth.set_access_token(account.access_token, account.secret_key)
#     api = tweepy.API(auth)
#     #user = api.me()
#
#     follower_ids = []
#     for follower in tweepy.Cursor(api.followers).items():
#         follower_ids.append(follower.id)
#
#     friend_ids = []
#     for friend in tweepy.Cursor(api.friends).items():
#         friend_ids.append(friend.id)
#
#     unfollow_list = get_diff(friend_ids, follower_ids)
#
#     for follower in unfollow_list:
#         Order.objects.create(user=account, func='unfollow_user', args='{},'.format(follower))
#     return u'Success'


# @periodic_task(run_every=crontab(minute="*/5"))
# def hashtags():
#     # you have to retreive hastags that last retrieved 2 hours ago
#     for hashtag in Hashtag.objects.filter(last_time_sync__lt=''):  # aggregate by hashtag
#         account = hashtag.created_user
#         auth = OAuthHandler(getattr(settings, 'TWITTER_CONSUMER_KEY'), getattr(settings, 'TWITTER_CONSUMER_SECRET'))
#         auth.set_access_token(account.access_token, account.secret_key)
#         api = tweepy.API(auth)
#         #user = api.me()
#         results = api.search(q=hashtag.hash_tag_key)
#         # sleep
#
#         for result in results:
#             if hashtag.retweet_or_favourite == 'R':
#                 Order.objects.create(user=account, func='rewteet', args='{},'.format(result.id))
#             else:
#                 Order.objects.create(user=account, func='fav', args='{},'.format(result.id))
#         hashtag.last_time_sync = datetime.datetime.now()
#         hashtag.save()
#         time.sleep(10)
#     return u'Success'
