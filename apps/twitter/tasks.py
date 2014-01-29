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
from django.utils import timezone

# setup logger
logger = get_task_logger(__name__)


@periodic_task(run_every=crontab(minute="*/1"))
def process_scheduled_orders():
    """ process_scheduled_orders """
    logger.debug('process_scheduled_orders is starting up')
    delta_time = datetime.datetime.utcnow().replace(tzinfo=utc) - datetime.timedelta(hours=1)
    delta_time = timezone.localtime(delta_time, timezone.get_current_timezone())
    auth = OAuthHandler(getattr(settings, 'TWITTER_CONSUMER_KEY'), getattr(settings, 'TWITTER_CONSUMER_SECRET'))

    for order in ScheduleOrder.objects.filter(
                    Q(Q(last_run__lte=delta_time) | Q(last_run__isnull=True)) & Q(run_once=False)):
        logger.debug('Order details: {}'.format(order.id))
        auth.set_access_token(order.user.access_token, order.user.secret_key)
        api = tweepy.API(auth)

        # black listed words
        black_listed_words = ["RT", u"♺"]

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
                                                 'tweet': tweet.text.encode('utf-8'),
                                                 'tweet_id': tweet.id,
                                                 'source_url': tweet.source_url,
                                                 'created_at': tweet.created_at,
                                                 'screen_name': tweet.author.screen_name.encode('utf-8')})
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
                                                 'tweet': tweet.text.encode('utf-8'),
                                                 'tweet_id': tweet.id,
                                                 'source_url': tweet.source_url,
                                                 'created_at': tweet.created_at,
                                                 'screen_name': tweet.author.screen_name.encode('utf-8')})
                    order.data[user] = last_id or order.data[user]
                    order.last_run = datetime.datetime.utcnow().replace(tzinfo=utc)
                    order.save()

        if order.func in ('retweet_search', 'favorite_search'):
            # if user is first timer
            if order.last_run is None:
                last_id = None

                timeline = []
                for tweet in api.search(q=u'{}'.format(order.args[0]), result_type='mixed', count='10'):
                    timeline.append(tweet)

                timeline = filter(lambda status: status.text[0] != "@", timeline)
                timeline = filter(lambda status: not any(word in status.text.split() for word in black_listed_words),
                                  timeline)

                for tweet in timeline:
                    if last_id is None:
                        last_id = tweet.id
                    Order.objects.create(user=order.user, func=order.kwargs['func'], args=[tweet.id, ],
                                         schedule_order=order,
                                         kwargs={
                                             'func': order.kwargs['func'],
                                             'tweet': tweet.text.encode('utf-8'),
                                             'tweet_id': tweet.id,
                                             'source_url': tweet.source_url,
                                             'created_at': tweet.created_at,
                                             'screen_name': tweet.author.screen_name.encode('utf-8')})
                order.data['last_id'] = last_id
                order.last_run = datetime.datetime.utcnow().replace(tzinfo=utc)
                order.save()
            else:
                # the hourly runs
                last_id = None
                logger.debug('Search hashtag: #{}'.format(order.args[0]))
                # for tweet in Cursor(api.search, q='#{}'.format(order.args[1]),
                #                     since_id=order.data['last_id']).items():
                timeline = []
                for tweet in api.search(q=u'{}'.format(order.args[0]), result_type='mixed',
                                        since_id=order.data['last_id'], count='10'):
                    timeline.append(tweet)

                timeline = filter(lambda status: status.text[0] != "@", timeline)
                timeline = filter(lambda status: not any(word in status.text.split() for word in black_listed_words),
                                  timeline)

                for tweet in timeline:
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

                order.data['last_id'] = last_id or order.data['last_id']
                order.last_run = datetime.datetime.utcnow().replace(tzinfo=utc)
                order.save()

    logger.info('process_scheduled_orders ended successfully')
    return u'Success'


@periodic_task(run_every=crontab(minute="*/1"))
def provision_orders():
    """ provision_orders """
    logger.debug('provision_orders is starting up')
    auth = OAuthHandler(getattr(settings, 'TWITTER_CONSUMER_KEY'), getattr(settings, 'TWITTER_CONSUMER_SECRET'))

    # first we get all the pending orders for a given user (users with pending orders > 0)
    for pending in Order.objects.values('user').filter(status=Order.PENDING).annotate(user_count=Count('user')).filter(
            user_count__gt=0):
        # get user threshold
        user_threshold = Twitter.objects.get(pk=pending.get('user')).user.threshold
        threshold = user_threshold / 24  # per hour
        now = timezone.localtime(timezone.now(), timezone.get_current_timezone())
        # get user hourly usage / return total number of executed commands in the given hour of the day
        # if hours do not exceed user threshold we continue
        hour_usage = Order.objects.filter(executed_at__year=now.year, executed_at__month=now.month,
                                          executed_at__day=now.day, executed_at__hour=now.hour,
                                          status__in=(Order.COMPLETED, Order.FAILED), user_id=pending.get('user'))

        hour_usage = hour_usage.count()
        logger.debug('provision_orders: user hourly usage: {}'.format(hour_usage))

        # skip user as he/she reached limit of hourly usage
        if hour_usage > threshold:
            continue
        for order in Order.objects.filter(status=Order.PENDING, user_id=pending.get('user'))[:1]:
            # only execute one command at a time
            try:
                auth.set_access_token(order.user.access_token, order.user.secret_key)
                api = tweepy.API(auth)
                if order.kwargs['func'] == 'retweet':
                    api.retweet(order.kwargs['tweet_id'])
                if order.kwargs['func'] == 'favorite':
                    api.create_favorite(order.kwargs['tweet_id'])
                order.status = order.COMPLETED
            except tweepy.TweepError:
                order.status = order.FAILED
            order.executed_at = datetime.datetime.utcnow().replace(tzinfo=utc)
            order.save()

    logger.info('provision_orders ended successfully')
    return u'Success'
